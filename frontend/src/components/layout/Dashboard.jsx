import { Box, Button, Container, Typography } from "@mui/material";

import AtmDataGrid from "../atms/AtmDataGrid";
import DiscrepancyDataGrid from "../serviceCalls/DiscrepancyDataGrid";
import ReliabilityMetrics from "../analytics/ReliabilityMetrics";
import MaintenanceFlags from "../analytics/MaintenanceFlags";
import ReportingLines from "../analytics/ReportingLines";
import LowCashAlert from "../analytics/LowCashAlert";
import ServiceCallDataGrid from "../serviceCalls/ServiceCallDataGrid";

import { useAuth } from "../../context/AuthContext";

export default function Dashboard() {
const { role, logout } = useAuth();

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

    <Button variant="outlined" onClick={logout}>
        Logout
    </Button>
    </Box>

    <Box sx={{ mb: 4 }}>
    <AtmDataGrid />
    </Box>
    <Box sx={{ mb: 4 }}>
  <ServiceCallDataGrid />
</Box>

    <Box sx={{ mb: 4 }}>
    <Typography variant="h5" sx={{ mb: 2 }}>
        Low Cash Alerts
    </Typography>

    <LowCashAlert />
    </Box>

    <Box sx={{ mb: 4 }}>
    <DiscrepancyDataGrid />
    </Box>

    <Box sx={{ mb: 4 }}>
    <Typography variant="h5" sx={{ mb: 2 }}>
        Reliability Metrics
    </Typography>

    <ReliabilityMetrics />
    </Box>

    <Box sx={{ mb: 4 }}>
    <Typography variant="h5" sx={{ mb: 2 }}>
        Maintenance Flags
    </Typography>

    <MaintenanceFlags />
    </Box>

    <Box sx={{ mb: 4 }}>
    <Typography variant="h5" sx={{ mb: 2 }}>
        Reporting Lines
    </Typography>

    <ReportingLines />
    </Box>
</Container>
);
}