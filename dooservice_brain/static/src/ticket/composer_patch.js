import { Composer } from "@mail/core/common/composer";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

import { TicketInfo } from "./ticket_info";

/** A closed ticket's composer says so: whatever is written there is refused by Dooservice anyway. */
patch(Composer.prototype, {
    get placeholder() {
        const thread = this.thread;
        if (thread?.model === "discuss.channel" && TicketInfo.shared?.get(thread.id)?.closed) {
            return _t("Ticket closed · to continue, open a new one linked to it");
        }
        return super.placeholder;
    },
});
