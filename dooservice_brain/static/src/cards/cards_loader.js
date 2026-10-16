/**
 * The pieces of many messages asked in one call, and Dooservice's partner asked once.
 *
 * Shared by every message, so it holds the web client's own ORM, never one bound to a
 * component: a message is destroyed and made again as the chat renders, and a call through
 * its ORM would then never answer. A call that fails answers "no pieces".
 */
export class CardsLoader {
    static shared = null;

    static of(orm) {
        CardsLoader.shared ??= new CardsLoader(orm);
        return CardsLoader.shared;
    }

    constructor(orm) {
        this.orm = orm;
        this.waiting = new Map();
        this.botPromise = null;
    }

    bot() {
        this.botPromise ??= this.orm.call("res.users", "dooservice_brain_bot", []).catch(() => false);
        return this.botPromise;
    }

    cards(messageId) {
        return new Promise((resolve) => {
            if (!this.waiting.size) {
                setTimeout(() => this.flush(), 0);
            }
            this.waiting.set(messageId, [...(this.waiting.get(messageId) || []), resolve]);
        });
    }

    async flush() {
        const waiting = this.waiting;
        this.waiting = new Map();
        const found = await this.orm.call("res.users", "dooservice_brain_cards", [[...waiting.keys()]]).catch(() => ({}));
        for (const [messageId, resolvers] of waiting) {
            resolvers.forEach((resolve) => resolve(found[messageId] || null));
        }
    }
}
