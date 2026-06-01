from __future__ import annotations
import random


# ─────────────────────────────────────────────
#  WhatsApp script engine
#
#  5 different message styles — one per DMI
#  category.  Each one hits the specific pain
#  point that matches that hall's situation.
#
#  Language style: natural Hinglish, short,
#  peer-to-peer, never salesy.
# ─────────────────────────────────────────────


def _script_digitally_invisible(name: str, area: str, leakage_pct: int, weakness: str) -> str:
    return (
        f"Namaste Bhai 🙏\n\n"
        f"Rohit Nate here — banquet operator from Dadar, also work with DigiVenue.\n\n"
        f"Aapka hall check kiya — *{name}*, {area}.\n"
        f"Google pe practically invisible hai abhi. Koi family 'banquet hall {area}' search kare toh aap dikhte hi nahi.\n\n"
        f"{'*Main problem: ' + weakness + '*' if weakness else ''}\n\n"
        f"Har mahine roughly *{leakage_pct}% inquiries* sirf is wajah se kho rahi hain.\n\n"
        f"Ek 2-page free snapshot bhejun kya — koi sales nahi, bas realistic picture. "
        f"Aap decide karo kya karna hai. 🙏"
    )


def _script_operationally_chaotic(name: str, area: str, leakage_pct: int, weakness: str) -> str:
    return (
        f"Namaste Bhai 🙏\n\n"
        f"Rohit Nate here — banquet operator, DigiVenue se.\n\n"
        f"*{name}* ke baare mein quick baat karni thi.\n"
        f"Hall ki Google presence toh hai, lekin inquiry management mein bahut leakage dikh rahi hai.\n\n"
        f"{'*Specifically: ' + weakness + '*' if weakness else ''}\n\n"
        f"Matlab *{leakage_pct}% log jo contact karte hain, unka follow-up nahi ho paata* — "
        f"booking kissi aur hall mein chali jaati hai.\n\n"
        f"Aapke operations ke hisaab se ek simple fix hai. Baat karein kya? No pressure. 🙏"
    )


def _script_visibility_weak(name: str, area: str, leakage_pct: int, weakness: str) -> str:
    return (
        f"Namaste Bhai 🙏\n\n"
        f"Rohit Nate — banquet wala, DigiVenue se.\n\n"
        f"*{name}* ka quick audit kiya — hall achha hai, lekin online presence weak lag rahi hai.\n\n"
        f"{'*Specifically: ' + weakness + '*' if weakness else ''}\n\n"
        f"Aajkal jo families venue dhundti hain — pehle Instagram/Google pe dekhti hain, *tab* call karti hain. "
        f"Agar wahan kuch dikhta nahi, toh call hi nahi aati.\n\n"
        f"*Competitor halls jo consistently reels dalte hain — unhe {leakage_pct}% zyada inquiries milti hain.*\n\n"
        f"2-minute call karein? Ek practical plan share karunga. 🙏"
    )


def _script_growth_ready(name: str, area: str, leakage_pct: int, weakness: str) -> str:
    return (
        f"Namaste Bhai 🙏\n\n"
        f"Rohit Nate here — DigiVenue.\n\n"
        f"*{name}* ka audit kiya — genuinely achha foundation hai. "
        f"Google presence hai, reviews bhi theek hain.\n\n"
        f"Ek specific gap dikh raha hai jo booking conversion rok raha hai:\n"
        f"{'*' + weakness + '*' if weakness else 'Content freshness aur inquiry workflow.'}\n\n"
        f"Yeh fix ho jaye toh *{leakage_pct}% zyada inquiries convert ho sakti hain* — "
        f"bina extra marketing spend ke.\n\n"
        f"Quick baat karein? 🙏"
    )


def _script_elite(name: str, area: str) -> str:
    return (
        f"Namaste Bhai 🙏\n\n"
        f"Rohit Nate — DigiVenue.\n\n"
        f"*{name}* ka audit kiya — genuinely strong digital presence hai. "
        f"Aap already top tier mein hain apne area mein.\n\n"
        f"Ek advanced conversation karni thi about vendor network aur referral systems — "
        f"woh next level hai jo abhi tak kisi hall ne properly implement nahi kiya.\n\n"
        f"Interest ho toh baat karein. 🙏"
    )


def whatsapp_script(row: dict) -> str:
    name = row.get('business_name', 'aapka hall')
    area = row.get('area', 'aapka area')
    category = row.get('dmi_category', 'Visibility Weak')
    leakage_pct = int(row.get('inquiry_leakage_probability', 0.4) * 100)

    # Pick the top weakness if available, else empty string
    weaknesses = row.get('key_weaknesses', [])
    weakness = weaknesses[0] if weaknesses else ''

    if category == 'Digitally Invisible':
        return _script_digitally_invisible(name, area, leakage_pct, weakness)
    elif category == 'Operationally Chaotic':
        return _script_operationally_chaotic(name, area, leakage_pct, weakness)
    elif category == 'Visibility Weak':
        return _script_visibility_weak(name, area, leakage_pct, weakness)
    elif category == 'Growth Ready':
        return _script_growth_ready(name, area, leakage_pct, weakness)
    else:
        return _script_elite(name, area)
