// Walk callers upward from given addresses and print each function with the strings it references.
// Args: <outfile> <depth> <hexaddr...>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class CallUp extends GhidraScript {
    PrintWriter out;
    Set<Function> seen = new HashSet<>();

    String asciiAt(Address a) {
        try {
            byte[] b = new byte[64];
            int n = currentProgram.getMemory().getBytes(a, b);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < n; i++) {
                int c = b[i] & 0xff;
                if (c == 0) break;
                if (c < 0x20 || c > 0x7e) return null;
                sb.append((char) c);
            }
            return sb.length() >= 4 ? sb.toString() : null;
        } catch (Exception e) { return null; }
    }

    Set<String> strings(Function f) {
        Set<String> s = new LinkedHashSet<>();
        for (Address a : f.getBody().getAddresses(true)) {
            for (Reference r : getReferencesFrom(a)) {
                if (!r.getReferenceType().isData()) continue;
                String t = asciiAt(r.getToAddress());
                if (t != null) s.add(t);
            }
        }
        return s;
    }

    void walk(Function f, int depth, int max, String indent) {
        out.println(indent + f.getName() + " @ " + f.getEntryPoint() + "  " + strings(f));
        if (!seen.add(f) || depth >= max) return;
        Set<Function> callers = new LinkedHashSet<>();
        Set<Address> noFunc = new LinkedHashSet<>();
        for (Reference r : getReferencesTo(f.getEntryPoint())) {
            Function c = getFunctionContaining(r.getFromAddress());
            if (c != null) callers.add(c); else noFunc.add(r.getFromAddress());
        }
        for (Address a : noFunc) out.println(indent + "  <- ref from " + a + " (no function)");
        for (Function c : callers) walk(c, depth + 1, max, indent + "  ");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        out = new PrintWriter(new FileWriter(args[0], true));
        int max = Integer.parseInt(args[1]);
        for (int i = 2; i < args.length; i++) {
            Address a = toAddr(Long.parseUnsignedLong(args[i].replace("0x", ""), 16));
            Function f = getFunctionContaining(a);
            if (f == null) { disassemble(a); f = createFunction(a, null); }
            out.println("=== " + args[i]);
            if (f != null) walk(f, 0, max, "");
            out.flush();
        }
        out.close();
    }
}
