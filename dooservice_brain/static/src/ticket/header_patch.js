import { ChatWindow } from "@mail/core/common/chat_window";
import { DiscussContent } from "@mail/core/public_web/discuss_content";

import { TicketBadge } from "./ticket_badge";

DiscussContent.components = { ...DiscussContent.components, TicketBadge };
ChatWindow.components = { ...ChatWindow.components, TicketBadge };
