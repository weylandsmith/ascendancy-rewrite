// disasm_range.java — disassemble [start,end) of the open program from raw bytes
// (force-disassemble every even byte gap), print "addr: bytes  mnemonic ops".
// Run headless via scripts/ghdra/run_disasm.sh. Usage:
//   analyzeHeadless <proj> ascend5 -process ascend_restored.bin -noanalysis \
//     -scriptPath scripts/ghdra -disasm_range <start> <end>
// GhidraMCP run_script_inline cannot bind a Python class implementing
// GhidraScript (confirmed TypeError t42) — this is the scripted path.
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;

public class disasm_range extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        long start = Long.parseUnsignedLong(args[0].replace("0x", ""), 16);
        long end   = Long.parseUnsignedLong(args[1].replace("0x", ""), 16);
        PrintWriter out = new PrintWriter(args.length > 2 ? args[2] : null);
        Listing listing = currentProgram.getListing();
        Address a = currentProgram.getAddressFactory()
            .getDefaultAddressSpace().getAddress(start);
        Address last = currentProgram.getAddressFactory()
            .getDefaultAddressSpace().getAddress(end);
        // force disassembly of the whole range (clears bad-data markers)
        go(new DisassembleCommand(a.minRawAddress()
            .newAddress(start), last, null, true));
        Instruction i = listing.getInstructionContaining(a);
        // walk forward from the instruction containing start
        long printed = 0;
        while (i != null && i.getAddress().compareTo(last) <= 0 && printed < 6000) {
            StringBuilder sb = new StringBuilder();
            sb.append(String.format("%05x: ", i.getAddress().getOffset()));
            byte[] ib = i.getBytes();
            StringBuilder hex = new StringBuilder();
            for (byte b : ib) hex.append(String.format("%02x", b));
            while (hex.length() < 20) hex.append(' ');
            sb.append(hex).append("  ");
            sb.append(i.getMnemonicString()).append(' ').append(i.toString().replace(i.getMnemonicString() + " ", ""));
            out.println(sb.toString());
            i = i.getNext();
            printed++;
        }
        out.close();
        printf("printed %d instructions 0x%x..0x%x -> %s%n", printed, start, end,
            args.length > 2 ? args[2] : "stdout");
    }
}
