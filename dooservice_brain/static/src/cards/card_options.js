import { _t } from "@web/core/l10n/translation";

/** What each kind of piece offers when the platform sends no options of its own. */
export const DEFAULT_OPTIONS = {
    resolved: [
        { value: "yes", label: _t("Yes, close") },
        { value: "no", label: _t("No, continue") },
    ],
    understood: [
        { value: "yes", label: _t("Yes, it is correct") },
        { value: "correct", label: _t("Correct"), input: true },
        { value: "cancel", label: _t("Cancel") },
    ],
    approval: [
        { value: "approve", label: _t("Approve") },
        { value: "decline", label: _t("Decline") },
    ],
    rating: [
        { value: "up", label: "👍" },
        { value: "down", label: "👎" },
    ],
};
