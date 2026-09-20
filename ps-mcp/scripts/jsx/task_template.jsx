// task_template.jsx - ps-mcp five-section task skeleton (S mode: return via toSource;
// F mode: additionally File.write this report to OUTDIR). Slots the driver MUST replace:
//   __OUTDIR__   -> quoted absolute AGENT_ output dir, e.g. "D:/somewhere/AGENT_out"
//   __TASKNAME__ -> quoted short task id, e.g. "retouch_portrait"
//   __PARAMS__   -> object literal of declared task parameters, e.g. { v: 1, keepLayers: true }
// Discipline map (ps-mcp SKILL iron laws): 1 source read-only / 2 AGENT_ duplicate /
// 3 snapshot before destructive / 4 report-only state / 5 whitelist+no-overwrite /
// 6 dialogs off first / 7 every write call into report.

// ---- 1. params (everything declared before any action) ----
app.displayDialogs = DialogModes.NO;
var OUTDIR = __OUTDIR__;
var TASK = __TASKNAME__;
var P = __PARAMS__;
var out = { task: TASK, params: P, steps: [], snapshots: [], exports: [], errors: [], na: [] };
function step(n, f) {
    try { out.steps.push(n + "=" + String(f())); return true; }
    catch (e) { out.errors.push(n + ":" + e); return false; }
}
function outDir() {
    var f = new Folder(OUTDIR);
    if (!f.exists) f.create();          // idempotent; OUTDIR was declared in intake
    return f.fsName;
}

// ---- 2. idempotent prep: agent duplicate of the active user document ----
var agent = null;
step("documentsPresent", function () { return app.documents.length; });
step("agentDuplicate", function () {
    if (app.documents.length === 0) { out.na.push("no document open"); return "NA"; }
    var src = app.activeDocument;
    for (var i = 0; i < app.documents.length; i++) {
        var d = app.documents[i];
        if (d.name.indexOf("AGENT_" + TASK + "_v") === 0) { agent = d; return "REUSED:" + d.name; }
    }
    agent = src.duplicate();
    agent.name = "AGENT_" + TASK + "_v" + (P.v || 1);
    src.close(SaveOptions.DONOTSAVECHANGES);   // user doc: never save agent edits into it
    return agent.name;
});

// ---- 3. helpers ----
function snapshot() {
    var f = new File(outDir() + "/" + agent.name + "_snap.psd");
    if (f.exists) return "SKIP: exists";
    agent.saveAs(f, new PSDSaveOptions(), true, Extension.LOWERCASE);
    out.snapshots.push(f.fsName);
    return "saved";
}
function exportPNG(name) {
    var f = new File(outDir() + "/" + name + ".png");
    if (f.exists) return "SKIP: target exists";
    var opt = new PNGSaveOptions();
    agent.saveAs(f, opt, true, Extension.LOWERCASE);
    out.exports.push(f.fsName);
    return f.fsName;
}

// ---- 4. operations (each destructive op: snapshot -> act -> report) ----
step("snapshotBeforeWork", function () { return snapshot(); });
// step("exampleOperation", function () { /* ... one op, return value into report ... */ });

// ---- 5. output ----
step("finalState", function () {
    return agent.name + " " + agent.width.as("px") + "x" + agent.height.as("px")
        + " mode=" + agent.mode + " profile=" + agent.colorProfileName;
});
var report = out.toSource();
if (String(OUTDIR) !== "") {
    var rf = new File(outDir() + "/" + TASK + "_report.json");
    if (!rf.exists) rf.encoding = "UTF-8";
    rf.open("w"); rf.write(report); rf.close();
}
report;
