import { Component, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const WIDTH = 300;
const HEIGHT = 140;
const COLORS = ["#714b67", "#017e84", "#e99d00", "#5b8def", "#d9534f", "#28a745"];

/** A chart counted by this Odoo with the person's access: bars, a line or a pie, drawn in SVG. */
export class DooserviceChart extends Component {
    static template = "dooservice_brain.Chart";
    static props = { card: Object, messageId: Number };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ groups: [], denied: "", loaded: false });
        this.width = WIDTH;
        this.height = HEIGHT;
        onMounted(async () => {
            const counted = await this.orm
                .call("res.users", "dooservice_brain_chart", [this.props.messageId, this.props.card.id])
                .catch(() => ({ denied: "unknown" }));
            Object.assign(this.state, { groups: counted.groups || [], denied: counted.denied || "", loaded: true });
        });
    }

    get top() {
        return Math.max(1, ...this.state.groups.map((group) => group.count));
    }

    get bars() {
        const step = WIDTH / Math.max(1, this.state.groups.length);
        return this.state.groups.map((group, index) => {
            const height = (group.count / this.top) * (HEIGHT - 20);
            return { ...group, x: index * step + 2, y: HEIGHT - height, width: step - 4, height, color: COLORS[0] };
        });
    }

    get points() {
        return this.bars.map((bar) => `${bar.x + bar.width / 2},${bar.y}`).join(" ");
    }

    get slices() {
        const total = this.state.groups.reduce((sum, group) => sum + group.count, 0) || 1;
        let angle = -Math.PI / 2;
        return this.state.groups.map((group, index) => {
            const start = angle;
            angle += (group.count / total) * Math.PI * 2;
            const large = angle - start > Math.PI ? 1 : 0;
            const [x1, y1, x2, y2] = [Math.cos(start), Math.sin(start), Math.cos(angle), Math.sin(angle)].map((value) => value * 60);
            const path = `M70,70 L${70 + x1},${70 + y1} A60,60 0 ${large} 1 ${70 + x2},${70 + y2} Z`;
            return { ...group, path, color: COLORS[index % COLORS.length] };
        });
    }
}
