/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Technical Service Dashboard Widget
 * Provides enhanced dashboard functionality for the technical service module
 */
export class TechnicalServiceDashboard extends Component {
    static template = "technical_service.Dashboard";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.rpc = useService("rpc");

        // Initialize dashboard data
        this.state = {
            openRequests: 0,
            criticalRequests: 0,
            slaBreached: 0,
            avgResolutionTime: 0,
            slaCompliance: 0,
            loading: true,
        };

        // Load dashboard data on mount
        this.loadDashboardData();
    }

    async loadDashboardData() {
        try {
            // Fetch dashboard statistics
            const stats = await this.rpc("/technical_service/dashboard/stats", {});

            this.state = {
                ...stats,
                loading: false,
            };

            this.render();
        } catch (error) {
            this.notification.add(_t("Failed to load dashboard data"), {
                type: "danger",
            });
            this.state.loading = false;
        }
    }

    /**
     * Navigate to critical requests
     */
    async viewCriticalRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Critical Requests"),
            res_model: "maintenance.request",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["x_priority_level", "=", "p1"]],
            context: {},
        });
    }

    /**
     * Navigate to SLA breached requests
     */
    async viewSLABreachedRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("SLA Breached Requests"),
            res_model: "maintenance.request",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["x_sla_status", "=", "breached"]],
            context: {},
        });
    }

    /**
     * Refresh dashboard data
     */
    async refreshDashboard() {
        this.state.loading = true;
        await this.loadDashboardData();

        this.notification.add(_t("Dashboard refreshed"), {
            type: "success",
        });
    }
}

// Register the widget
registry.category("view_widgets").add("technical_service_dashboard", TechnicalServiceDashboard);

/**
 * SLA Timer Widget
 * Shows countdown timer for SLA deadlines
 */
export class SLATimerWidget extends Component {
    static template = "technical_service.SLATimer";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.state = {
            timeRemaining: "",
            status: "on_track",
        };

        // Start timer
        this.updateTimer();
        this.timerInterval = setInterval(() => this.updateTimer(), 60000); // Update every minute
    }

    updateTimer() {
        const deadline = this.props.record.data[this.props.name];
        if (!deadline) return;

        const now = new Date();
        const deadlineDate = new Date(deadline);
        const diff = deadlineDate - now;

        if (diff <= 0) {
            this.state.timeRemaining = _t("Breached");
            this.state.status = "breached";
        } else {
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

            this.state.timeRemaining = _t("%s hours %s minutes", hours, minutes);

            // Determine status based on time remaining
            if (hours < 2) {
                this.state.status = "at_risk";
            } else {
                this.state.status = "on_track";
            }
        }

        this.render();
    }

    willUnmount() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
    }
}

// Register the SLA timer widget
registry.category("view_widgets").add("sla_timer", SLATimerWidget);

/**
 * Team Workload Chart Widget
 * Displays team workload distribution
 */
export class TeamWorkloadChart extends Component {
    static template = "technical_service.TeamWorkloadChart";
    static props = {
        teams: Array,
    };

    setup() {
        this.chartService = useService("chart");
        this.renderChart();
    }

    renderChart() {
        const chartData = {
            labels: this.props.teams.map(team => team.name),
            datasets: [{
                label: _t("Active Requests"),
                data: this.props.teams.map(team => team.active_requests),
                backgroundColor: "rgba(54, 162, 235, 0.5)",
                borderColor: "rgba(54, 162, 235, 1)",
                borderWidth: 1,
            }, {
                label: _t("Pending Requests"),
                data: this.props.teams.map(team => team.pending_requests),
                backgroundColor: "rgba(255, 206, 86, 0.5)",
                borderColor: "rgba(255, 206, 86, 1)",
                borderWidth: 1,
            }],
        };

        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                    },
                },
            },
            plugins: {
                legend: {
                    position: "top",
                },
                tooltip: {
                    mode: "index",
                    intersect: false,
                },
            },
        };

        this.chartService.renderChart("teamWorkloadChart", {
            type: "bar",
            data: chartData,
            options: chartOptions,
        });
    }
}

// Register the team workload chart widget
registry.category("view_widgets").add("team_workload_chart", TeamWorkloadChart);

/**
 * Quick Create Request Widget
 * Allows quick creation of service requests from dashboard
 */
export class QuickCreateRequest extends Component {
    static template = "technical_service.QuickCreateRequest";
    static props = {
        record: { type: Object, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = {
            requestType: "incident",
            priority: "p3",
            description: "",
        };
    }

    async createRequest() {
        if (!this.state.description) {
            this.notification.add(_t("Please enter a description"), {
                type: "warning",
            });
            return;
        }

        try {
            const requestId = await this.orm.create("maintenance.request", {
                name: this.state.description,
                x_request_type: this.state.requestType,
                x_priority_level: this.state.priority,
                description: this.state.description,
                request_date: new Date().toISOString(),
            });

            this.notification.add(_t("Request created successfully"), {
                type: "success",
            });

            // Open the created request
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "maintenance.request",
                res_id: requestId,
                view_mode: "form",
                views: [[false, "form"]],
            });

            // Reset form
            this.state = {
                requestType: "incident",
                priority: "p3",
                description: "",
            };
        } catch (error) {
            this.notification.add(_t("Failed to create request"), {
                type: "danger",
            });
        }
    }
}

// Register the quick create widget
registry.category("view_widgets").add("quick_create_request", QuickCreateRequest);