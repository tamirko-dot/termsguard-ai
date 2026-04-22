const HIGHLIGHT_COLORS = { red: "#fed7d7", yellow: "#fefcbf", green: "#c6f6d5" };
const HIGHLIGHT_CLASS = "termsguard-highlight";

export function highlightFinding(sourceQuote, risk) {
  const color = HIGHLIGHT_COLORS[risk] || "#e2e8f0";
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;

  while ((node = walker.nextNode())) {
    const idx = node.textContent.indexOf(sourceQuote);
    if (idx === -1) continue;

    const range = document.createRange();
    range.setStart(node, idx);
    range.setEnd(node, idx + sourceQuote.length);

    const mark = document.createElement("mark");
    mark.className = HIGHLIGHT_CLASS;
    mark.style.cssText = `background:${color}; border-radius:2px; padding:0 2px;`;
    range.surroundContents(mark);

    mark.scrollIntoView({ behavior: "smooth", block: "center" });
    return true;
  }
  return false;
}

export function clearHighlights() {
  document.querySelectorAll(`.${HIGHLIGHT_CLASS}`).forEach((el) => {
    el.replaceWith(...el.childNodes);
  });
}
