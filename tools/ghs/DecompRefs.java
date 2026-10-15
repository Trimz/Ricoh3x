// Decompile functions selected by: "s:<string literal>" (functions referencing it),
// "a:<hex address>" (function containing it), "n:<name substring>", "c:<name substring>" (callers).
// Args: <outfile> <items...>
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class DecompRefs extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0], true));
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        Set<Function> done = new HashSet<>();
        Listing listing = currentProgram.getListing();
        for (int i = 1; i < args.length; i++) {
            String it = args[i];
            List<Function> fns = new ArrayList<>();
            if (it.startsWith("c:")) {
                String sub = it.substring(2);
                for (Function f : listing.getFunctions(true)) {
                    if (!f.getName(true).contains(sub)) continue;
                    for (Reference r : getReferencesTo(f.getEntryPoint())) {
                        Function c = getFunctionContaining(r.getFromAddress());
                        out.println("### CALLER of " + f.getName(true) + " from " + r.getFromAddress() + " in " + (c == null ? "?" : c.getName(true) + " @ " + c.getEntryPoint()));
                        if (c != null) fns.add(c);
                    }
                }
            } else if (it.startsWith("n:")) {
                String sub = it.substring(2);
                for (Function f : listing.getFunctions(true)) {
                    String nm = f.getName(true);
                    if (nm.contains(sub)) { fns.add(f); out.println("### NAME " + sub + " -> " + nm + " @ " + f.getEntryPoint()); }
                }
            } else if (it.startsWith("a:")) {
                Address a = toAddr(Long.parseUnsignedLong(it.substring(2).replace("0x", ""), 16));
                Function f = getFunctionContaining(a);
                if (f == null) { disassemble(a); f = createFunction(a, null); }
                if (f != null) fns.add(f);
                out.println("### ADDR " + it + " -> " + (f == null ? "no function" : f.getName() + " @ " + f.getEntryPoint()));
            } else {
                String text = it.substring(2);
                byte[] needle = (text + "\0").getBytes("ISO-8859-1");
                Address cur = currentProgram.getMinAddress();
                while (true) {
                    Address hit = currentProgram.getMemory().findBytes(cur, needle, null, true, monitor);
                    if (hit == null) break;
                    out.println("### STRING \"" + text + "\" @ " + hit);
                    for (Reference r : getReferencesTo(hit)) {
                        Function f = getFunctionContaining(r.getFromAddress());
                        out.println("    ref from " + r.getFromAddress() + " in " + (f == null ? "?" : f.getName() + "@" + f.getEntryPoint()));
                        if (f != null) fns.add(f);
                    }
                    cur = hit.add(1);
                }
            }
            for (Function f : fns) {
                if (!done.add(f)) continue;
                DecompileResults res = di.decompileFunction(f, 120, monitor);
                out.println("// ===== " + f.getName() + " @ " + f.getEntryPoint());
                out.println(res.decompileCompleted() ? res.getDecompiledFunction().getC() : "// decompile failed: " + res.getErrorMessage());
            }
            out.flush();
        }
        out.close();
    }
}
