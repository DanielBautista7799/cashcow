import { useEffect, useState } from "react";
import {
Box,
Button,
Card,
CardContent,
Container,
Tab,
Tabs,
Typography,
} from "@mui/material";

import AtmDataGrid from "../atms/AtmDataGrid";
import DiscrepancyDataGrid from "../serviceCalls/DiscrepancyDataGrid";
import ReliabilityMetrics from "../analytics/ReliabilityMetrics";
import MaintenanceFlags from "../analytics/MaintenanceFlags";
import ReportingLines from "../analytics/ReportingLines";
import LowCashAlert from "../analytics/LowCashAlert";
import ServiceCallDataGrid from "../serviceCalls/ServiceCallDataGrid";

import { useAuth } from "../../context/AuthContext";
import api from "../../api/client";

export default function Dashboard() {
const { role, logout } = useAuth();

// Controls which dashboard tab is currently shown
const [tab, setTab] = useState(0);

const [summary, setSummary] = useState({
activeAtms: 0,
lowCashAtms: 0,
activeServiceCalls: 0,
maintenanceFlags: 0,
});

const [summaryLoading, setSummaryLoading] = useState(true);

// Gets the values shown in the overview cards
useEffect(() => {
async function fetchSummary() {
    try {
    const atmResponse = await api.get("/atms");

    const lowCashResponse = await api.get("/atms", {
        params: {
        max_cash: 20,
        },
    });

    const serviceCallResponse = await api.get(
        "/service-call"
    );

    const maintenanceResponse = await api.get(
        "/branches/maintenance-flags"
    );

    const activeServiceCalls =
        serviceCallResponse.data.filter(
        (serviceCall) =>
            serviceCall.status === "Pending" ||
            serviceCall.status === "In-Progress"
        ).length;

    setSummary({
        activeAtms: atmResponse.data.length,
        lowCashAtms: lowCashResponse.data.length,
        activeServiceCalls: activeServiceCalls,
        maintenanceFlags:
        maintenanceResponse.data.length,
    });
    } catch (error) {
    console.error(error);
    } finally {
    setSummaryLoading(false);
    }
}

fetchSummary();
}, []);

return (
<Container sx={{ mt: 4, mb: 4 }}>
    <Box
    sx={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        mb: 3,
    }}
    >
    <Box>
        <Typography variant="h4">
        CashCow ATM Command Center
        </Typography>

        <Typography>
        Role: {role}
        </Typography>
    </Box>

    <Button
        variant="outlined"
        onClick={logout}
    >
        Logout
    </Button>
    </Box>

    {/* Switch between the main dashboard sections */}
    <Tabs
    value={tab}
    onChange={(event, newValue) =>
        setTab(newValue)
    }
    sx={{
        mb: 4,
        borderBottom: 1,
        borderColor: "divider",
    }}
    >
    <Tab label="Overview" />
    <Tab label="Operations" />
    <Tab label="Analytics" />
    </Tabs>

    {/* Overview Tab */}
    {tab === 0 && (
    <Box>
        <Box
        sx={{
            display: "grid",
            gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            md: "repeat(4, 1fr)",
            },
            gap: 2,
            mb: 4,
        }}
        >
        <Card>
            <CardContent>
            <Typography color="text.secondary">
                Active ATMs
            </Typography>

            <Typography variant="h4">
                {summaryLoading
                ? "..."
                : summary.activeAtms}
            </Typography>
            </CardContent>
        </Card>

        <Card>
            <CardContent>
            <Typography color="text.secondary">
                Low Cash ATMs
            </Typography>

            <Typography
                variant="h4"
                color={
                summary.lowCashAtms > 0
                    ? "error"
                    : "inherit"
                }
            >
                {summaryLoading
                ? "..."
                : summary.lowCashAtms}
            </Typography>
            </CardContent>
        </Card>

        <Card>
            <CardContent>
            <Typography color="text.secondary">
                Active Service Calls
            </Typography>

            <Typography variant="h4">
                {summaryLoading
                ? "..."
                : summary.activeServiceCalls}
            </Typography>
            </CardContent>
        </Card>

        <Card>
            <CardContent>
            <Typography color="text.secondary">
                Maintenance Flags
            </Typography>

            <Typography
                variant="h4"
                color={
                summary.maintenanceFlags > 0
                    ? "warning.main"
                    : "inherit"
                }
            >
                {summaryLoading
                ? "..."
                : summary.maintenanceFlags}
            </Typography>
            </CardContent>
        </Card>
        </Box>

        <Box sx={{ mb: 4 }}>
        <Typography
            variant="h5"
            sx={{ mb: 1 }}
        >
            Low Cash Alerts
        </Typography>

        <Typography
            color="text.secondary"
            sx={{ mb: 2 }}
        >
            Active ATMs with less than 20% cash
            remaining.
        </Typography>

        <LowCashAlert />
        </Box>

        <Box sx={{ mb: 4 }}>
        <Typography
            variant="h5"
            sx={{ mb: 1 }}
        >
            Maintenance Flags
        </Typography>

        <Typography
            color="text.secondary"
            sx={{ mb: 2 }}
        >
            Branches with more than 30% of their
            ATMs in Maintenance.
        </Typography>

        <MaintenanceFlags />
        </Box>
    </Box>
    )}

    {/* Operations Tab */}
    {tab === 1 && (
    <Box>
        <Box sx={{ mb: 4 }}>
        <AtmDataGrid />
        </Box>

        <Box sx={{ mb: 4 }}>
        <ServiceCallDataGrid />
        </Box>
    </Box>
    )}

    {/* Analytics Tab */}
    {tab === 2 && (
    <Box>
        <Box sx={{ mb: 4 }}>
        <Typography
            variant="h5"
            sx={{ mb: 1 }}
        >
            Co-Location Discrepancies
        </Typography>

        <Typography
            color="text.secondary"
            sx={{ mb: 2 }}
        >
            Service calls where the ATM and technician
            are assigned to different branches.
        </Typography>

        <DiscrepancyDataGrid />
        </Box>

        <Box sx={{ mb: 4 }}>
        <Typography
            variant="h5"
            sx={{ mb: 1 }}
        >
            Reliability Metrics
        </Typography>

        <Typography
            color="text.secondary"
            sx={{ mb: 2 }}
        >
            Completed and failed service calls grouped by
            ATM model.
        </Typography>

        <ReliabilityMetrics />
        </Box>

        <Box sx={{ mb: 4 }}>
        <Typography
            variant="h5"
            sx={{ mb: 1 }}
        >
            Reporting Lines
        </Typography>

        <Typography
            color="text.secondary"
            sx={{ mb: 2 }}
        >
            Technicians reporting to a supervisor and
            their active service calls.
        </Typography>

        <ReportingLines />
        </Box>
    </Box>
    )}
</Container>
);
}