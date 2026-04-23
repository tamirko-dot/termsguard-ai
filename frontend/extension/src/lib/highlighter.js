const HIGHLIGHT_COLORS = { red: "#fed7d7", yellow: "#fefcbf", green: "#c6f6d5" };
const HIGHLIGHT_CLASS = "termsguard-highlight";

export function highlightFinding(sourceQuote, risk) {
    const color = HIGHLIGHT_COLORS[risk] || "#e2e8f0";

    // Try progressively shorter substrings until one matches
    const candidates = [
        sourceQuote,
        sourceQuote.slice(0, 120).trim(),
        sourceQuote.slice(0, 80).trim(),
        sourceQuote.slice(0, 50).trim(),
    ];

    for (const text of candidates) {
        if (text.length < 15) break;
        if (_tryHighlight(text, color)) return true;
    }
    return false;
}

function _tryHighlight(text, color) {
    // window.find() handles cross-node text — far more reliable than TreeWalker
    if (!window.find(text, false, false, true, false, false, false)) return false;

    const selection = window.getSelection();
    if (!selection || !selection.rangeCount) return false;

    const range = selection.getRangeAt(0);

    try {
        const mark = document.createElement("mark");
        mark.className = HIGHLIGHT_CLASS;
        mark.style.cssText = `background:${color}; border-radius:3px; padding:1px 3px; color:inherit;`;
        range.surroundContents(mark);
        mark.scrollIntoView({ behavior: "smooth", block: "center" });
        selection.removeAllRanges();
        return true;
    } catch {
        // Range spans multiple nodes — just scroll to it
        const el = range.startContainer.parentElement;
        if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
        selection.removeAllRanges();
        return true; // still counts as success — user can see the location
    }
}

export function clearHighlights() {
    document.querySelectorAll(`.${HIGHLIGHT_CLASS}`).forEach((el) => {
        el.replaceWith(...el.childNodes);
    });
}
