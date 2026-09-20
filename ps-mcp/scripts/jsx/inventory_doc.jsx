// inventory_doc.jsx - ps-mcp G0 document inventory (read-only; optional preview export)
// Slots: __OUTDIR__ (replaced by driver with quoted output dir; "" = skip preview export)
// Discipline: never writes outside declared OUTDIR; never touches user document state;
//             preview export only when a document exists and target file absent.
app.displayDialogs = DialogModes.NO;

var OUTDIR = __OUTDIR__;
var out = { probe: "inventory_doc.jsx", documents: [], steps: [] };
function step(n, f) {
    try { out.steps.push(n + "=" + String(f())); } catch (e) { out.steps.push(n + "=ERR:" + e); }
}

function layerRow(l, depth) {
    // one row per layer/set; user layer names reported verbatim (never renamed/guessed)
    var row = { depth: depth, typename: l.typename, name: l.name,
                visible: String(l.visible) };
    try { row.locked = String(l.allLocked); } catch (e) { row.locked = "n/a"; }
    try { row.kind = String(l.kind); } catch (e) { row.kind = "n/a"; }
    return row;
}

function walkLayers(coll, depth, acc, cap) {
    for (var i = 0; i < coll.length; i++) {
        if (acc.rows.length >= cap.max) { acc.truncated = true; return; }
        var l = coll[i];
        acc.rows.push(layerRow(l, depth));
        if (l.typename === "LayerSet") { walkLayers(l.layers, depth + 1, acc, cap); }
    }
}

step("documentsCount", function () { return app.documents.length; });

for (var d = 0; d < app.documents.length; d++) {
    (function () {
        var doc = app.documents[d];
        var info = { index: d, name: doc.name };
        try { info.widthPx = doc.width.as("px"); } catch (e) { info.widthPx = "ERR"; }
        try { info.heightPx = doc.height.as("px"); } catch (e) { info.heightPx = "ERR"; }
        try { info.resolution = doc.resolution; } catch (e) { info.resolution = "ERR"; }
        try { info.mode = String(doc.mode); } catch (e) { info.mode = "ERR"; }
        try { info.colorProfileName = doc.colorProfileName; } catch (e) { info.colorProfileName = "ERR:" + e; }
        try { info.historyStates = doc.historyStates.length; } catch (e) { info.historyStates = "ERR"; }
        var acc = { rows: [], truncated: false };
        var cap = { max: 200 };
        try { walkLayers(doc.layers, 0, acc, cap); } catch (e) { acc.err = String(e); }
        info.layerRows = acc.rows;
        info.layerTruncated = acc.truncated;
        var smart = 0;
        for (var r = 0; r < acc.rows.length; r++) {
            if (acc.rows[r].kind === "LayerKind.SMARTOBJECT") smart++;
        }
        info.smartObjects = smart;
        out.documents.push(info);

        // optional low-res preview export (G0 look-at obligation), target-absent check first
        if (OUTDIR !== "") {
            step("previewDoc" + d, function () {
                var f = new File(OUTDIR + "/AGENT_inventory_preview_doc" + d + ".png");
                if (f.exists) return "SKIP: target exists";
                var opt = new PNGSaveOptions();
                doc.saveAs(f, opt, true, Extension.LOWERCASE);
                return f.fsName;
            });
        }
    })();
}

out.toSource();
