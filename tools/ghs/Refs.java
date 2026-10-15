// List all references to each address (and +4 steps). Args: <outfile> <addr[:count]>...
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class Refs extends GhidraScript {
    @Override protected void run() throws Exception {
        String[] a = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(a[0], true));
        for (int i = 1; i < a.length; i++) {
            String[] p = a[i].split(":");
            long base = Long.decode(p[0]); int n = p.length > 1 ? Integer.parseInt(p[1]) : 1;
            for (int k = 0; k < n; k++) {
                var ad = toAddr(base + 4L * k);
                for (Reference r : getReferencesTo(ad)) {
                    Function f = getFunctionContaining(r.getFromAddress());
                    out.println(ad + " <- " + r.getFromAddress() + " " + r.getReferenceType() + " in " + (f == null ? "?" : f.getName() + "@" + f.getEntryPoint()));
                }
            }
        }
        out.close();
    }
}
