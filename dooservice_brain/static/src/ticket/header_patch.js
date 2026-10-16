import { ChatWindow } from "@mail/core/common/chat_window";
import { Discuss } from "@mail/core/common/discuss";

import { TicketBadge } from "./ticket_badge";

Discuss.components = { ...Discuss.components, TicketBadge };
ChatWindow.components = { ...ChatWindow.components, TicketBadge };
