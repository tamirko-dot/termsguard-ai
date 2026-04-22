const TOS_URL_PATTERN = /terms|privacy|tos|eula|legal|policy/i;
const AGREE_PATTERNS = [/i agree/i, /accept terms/i, /agree to/i];

export function isToSPage() {
  if (TOS_URL_PATTERN.test(window.location.href)) return true;

  const bodyText = document.body?.innerText || "";
  const hasAgreeButton = AGREE_PATTERNS.some((p) => p.test(bodyText));
  const hasAgreeCheckbox = !!document.querySelector(
    'input[type="checkbox"][id*="agree"], input[type="checkbox"][name*="agree"]'
  );

  return hasAgreeButton || hasAgreeCheckbox;
}

export function extractText() {
  return document.body?.innerText || "";
}
