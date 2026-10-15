import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { user } from "@web/core/user";
import { useService } from "@web/core/utils/hooks";

export class AssistantSystray extends Component {
    static template = "dooservice_brain.AssistantSystray";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.store = useService("mail.store");
        this.state = useState({ allowed: false });
        onWillStart(async () => {
            this.state.allowed = await user.hasGroup("dooservice_brain.group_ask");
        });
    }

    async open() {
        const screenModel = this.action.currentController?.action?.res_model || "";
        const partnerId = await this.orm.call("res.users", "dooservice_brain_open", [screenModel]);
        if (partnerId) {
            await this.store.openChat({ partnerId });
        }
    }
}

registry.category("systray").add("dooservice_brain.assistant", { Component: AssistantSystray }, { sequence: 30 });
