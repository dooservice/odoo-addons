import { NewTicketDialog } from "./new_ticket_dialog";

/** The way into a ticket from anywhere in the client: the bulb, a list button, a closed chat. */
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

    async openChannel(channelId) {
        const store = this.env.services["mail.store"];
        const thread = await store.Thread.getOrFetch({ model: "discuss.channel", id: channelId });
        if (thread) {
            thread.open({ focus: true });
        }
    }
}
