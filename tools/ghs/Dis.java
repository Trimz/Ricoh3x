// Print disassembly for ranges. Args: <outfile> <start:end>...
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;

public class Dis extends GhidraScript {
    @Override protected void run() throws Exception {
        String[] a = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(a[0], true));
        for (int i = 1; i < a.length; i++) {
            String[] p = a[i].split(":");
            Address s = toAddr(Long.parseUnsignedLong(p[0].replace("0x",""),16));
            Address e = toAddr(Long.parseUnsignedLong(p[1].replace("0x",""),16));
            out.println("=== " + a[i]);
            Listing l = currentProgram.getListing();
            for (Address x = s; x.compareTo(e) < 0; ) {
                CodeUnit cu = l.getCodeUnitAt(x);
                if (cu == null) { x = x.add(1); continue; }
                StringBuilder sb = new StringBuilder(x + "  " + cu.toString());
                for (Reference r : cu.getReferencesFrom()) sb.append("   -> " + r.getToAddress());
                Function f = getFunctionAt(x);
                if (f != null) out.println("-- function " + f.getName());
                out.println(sb);
                x = x.add(cu.getLength());
            }
        }
        out.close();
    }
}
