/** @odoo-module **/

import { NewTicketDialog } from "./new_ticket_dialog";

/** The way into a ticket from anywhere in the client: the bulb, a list button, a closed chat's link. */
export class TicketOpener {
    constructor(env) {
        this.env = env;
    }

    /** The screen the person is on: its model and, on a form, the record open in it. */
    screen() {
        const controller = this.env.services.action.currentController;
        const model = controller?.action?.res_model || "";
        const recordId = Number.isInteger(controller?.props?.resId) ? controller.props.resId : 0;
        return { screenModel: model, recordId };
    }

    ask(extra = {}) {
        const onOpened = (channelId) => this.openChannel(channelId);
        this.env.services.dialog.add(NewTicketDialog, { ...this.screen(), onOpened, ...extra });
    }

    /** Odoo 16 keeps its chats in the messaging models: the channel is fetched there, then opened. */
    async openChannel(channelId) {
        const messaging = await this.env.services.messaging.get();
        const channels = await messaging.models["Thread"].performRpcChannelInfo({ ids: [channelId] });
        if (channels[0]) {
            channels[0].open();
        }
    }
}
