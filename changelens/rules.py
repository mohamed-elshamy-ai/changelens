"""Rule lists used to judge how much a change matters. English and Arabic."""
import re

IMPORTANT_WORDS = [
    # money and payment
    "payment", "pay", "fee", "fees", "price", "cost", "refund", "invoice", "penalty", "penalties", "interest", "deposit", "salary",
    # time limits
    "deadline", "due", "within", "days", "months", "term", "renew", "renewal", "expire", "expiry",
    # ending / liability
    "terminate", "termination", "cancel", "cancellation", "liability", "liable", "indemnify", "indemnity", "breach", "warranty", "damages",
    # legal / control
    "confidential", "confidentiality", "exclusive", "governing law", "jurisdiction", "arbitration", "assign", "non-compete", "waive",
    # Arabic
    "دفع", "سداد", "رسوم", "سعر", "تكلفة", "غرامة", "فوائد", "مهلة", "موعد", "مدة", "تجديد", "إنهاء", "فسخ", "إلغاء", "مسؤولية", "تعويض", "سرية", "حصري", "قانون", "تحكيم",
]
_word_res = [re.compile(r"(?<!\w)" + re.escape(w) + r"(?!\w)", re.I) for w in IMPORTANT_WORDS]

# obligation strength, strongest to weakest
STRENGTH = {"must": 3, "shall": 3, "required": 3, "will": 2, "should": 2, "may": 1, "can": 1, "optional": 0,
            "يجب": 3, "يلتزم": 3, "ينبغي": 2, "يجوز": 1, "يمكن": 1}
NEGATIONS = ["not", "no", "never", "without", "neither", "لا", "لن", "بدون", "غير"]

NUMBER = re.compile(r"(?<![\w.])[$€£]?\d[\d,]*(?:\.\d+)?%?")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")


def normalize_digits(s):
    return s.translate(ARABIC_DIGITS)


def has_important_word(text):
    return [w for w, rx in zip(IMPORTANT_WORDS, _word_res) if rx.search(text)]


def numbers(text):
    return [n.replace(",", "") for n in NUMBER.findall(normalize_digits(text))]
