// Pre-analysis setup for the GR IIIx RTOS image (raw ARMv7 blob at 0x53000000).
import ghidra.app.script.GhidraScript;

public class Prep extends GhidraScript {
    @Override
    protected void run() throws Exception {
        setAnalysisOption(currentProgram, "ARM Aggressive Instruction Finder", "true");
        disassemble(toAddr(0x53000000L));
        createFunction(toAddr(0x53000000L), "reset_vectors");
    }
}
