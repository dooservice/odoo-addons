import { Component, onWillStart, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

/** The three things a person opens a ticket for, as the bulb offers them. */
const KINDS = [
    { value: "question", icon: "💬", label: _t("Question"), hint: _t("How something is done") },
    { value: "incident", icon: "⚠️", label: _t("Incident"), hint: _t("Something did not go as expected") },
    { value: "change", icon: "⚙️", label: _t("Change"), hint: _t("Make the system do something different") },
];

/** «New ticket»: its kind, what happens, and the screen it is opened from, attached. */
export class NewTicketDialog extends Component {
    static template = "dooservice_brain.NewTicketDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        screenModel: { type: String, optional: true },
        recordId: { type: Number, optional: true },
        continues: { type: Number, optional: true },
        continuesNumber: { type: String, optional: true },
        onOpened: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.kinds = KINDS;
        this.state = useState({ kind: "question", text: "", screen: "", status: null, busy: false });
        onWillStart(async () => {
            const [status, screen] = await Promise.all([
                this.orm.call("res.users", "dooservice_brain_status", []),
                this.props.screenModel
                    ? this.orm.call("dooservice.ticket", "screen_label", [this.props.screenModel, this.props.recordId || 0])
                    : "",
            ]);
            this.state.status = status;
            this.state.screen = screen || "";
        });
    }

    get title() {
        return _t("New ticket for Dooservice");
    }

    get canOpen() {
        return Boolean(this.state.status?.ready && this.state.text.trim() && !this.state.busy);
    }

    async open() {
        if (!this.canOpen) {
            return;
        }
        this.state.busy = true;
        try {
            const opened = await this.orm.call("dooservice.ticket", "open_ticket", [
                this.state.kind,
                this.state.text.trim(),
                this.props.screenModel || "",
                this.props.recordId || 0,
                this.props.continues || null,
            ]);
            this.props.close();
            await this.props.onOpened?.(opened.channel_id);
        } finally {
            this.state.busy = false;
        }
    }
}
