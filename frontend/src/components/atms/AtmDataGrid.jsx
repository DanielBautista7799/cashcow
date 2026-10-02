import { useEffect, useState } from "react";
import {
Box,
Button,
Dialog,
DialogActions,
DialogContent,
DialogTitle,
MenuItem,
Stack,
TextField,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

import { useAuth } from "../../context/AuthContext";
import api from "../../api/client";

export default function AtmDataGrid() {
const { role } = useAuth();

const [atms, setAtms] = useState([]);
const [dialogOpen, setDialogOpen] = useState(false);

const [formValues, setFormValues] = useState({
serial_number: "",
model: "",
status: "Operational",
cash_level: "",
branch_id: "",
});

async function fetchAtms() {
const response = await api.get("/atms");
setAtms(response.data);
}

useEffect(() => {
fetchAtms();
}, []);

const handleFieldChange = (field) => (event) => {
setFormValues({
    ...formValues,
    [field]: event.target.value,
});
};

const handleSubmit = async () => {
await api.post("/atms", {
    ...formValues,
    cash_level: Number(formValues.cash_level),
    branch_id: Number(formValues.branch_id),
});

setDialogOpen(false);

setFormValues({
    serial_number: "",
    model: "",
    status: "Operational",
    cash_level: "",
    branch_id: "",
});

await fetchAtms();
};

const columns = [
{ field: "id", headerName: "ID", width: 70 },
{ field: "serial_number", headerName: "Serial Number", width: 150 },
{ field: "model", headerName: "Model", width: 150 },
{ field: "status", headerName: "Status", width: 150 },
{ field: "cash_level", headerName: "Cash Level", width: 130 },
{ field: "branch_id", headerName: "Branch ID", width: 110 },
];

return (
<Box>
    {role === "Admin" && (
    <Button
        variant="outlined"
        sx={{ mb: 2 }}
        onClick={() => setDialogOpen(true)}
    >
        Add ATM
    </Button>
    )}

    <Box sx={{ height: 500, width: "100%" }}>
    <DataGrid
        rows={atms}
        columns={columns}
        getRowId={(row) => row.id}
    />
    </Box>

    <Dialog
    open={dialogOpen}
    onClose={() => setDialogOpen(false)}
    >
    <DialogTitle>Add New ATM</DialogTitle>

    <DialogContent>
        <Stack spacing={2} sx={{ mt: 1, minWidth: 300 }}>
        <TextField
            label="Serial Number"
            value={formValues.serial_number}
            onChange={handleFieldChange("serial_number")}
        />

        <TextField
            label="Model"
            value={formValues.model}
            onChange={handleFieldChange("model")}
        />

        <TextField
            select
            label="Status"
            value={formValues.status}
            onChange={handleFieldChange("status")}
        >
            <MenuItem value="Operational">Operational</MenuItem>
            <MenuItem value="In-Transport">In-Transport</MenuItem>
            <MenuItem value="Maintenance">Maintenance</MenuItem>
            <MenuItem value="Offline">Offline</MenuItem>
        </TextField>

        <TextField
            label="Cash Level"
            type="number"
            value={formValues.cash_level}
            onChange={handleFieldChange("cash_level")}
        />

        <TextField
            label="Branch ID"
            type="number"
            value={formValues.branch_id}
            onChange={handleFieldChange("branch_id")}
        />
        </Stack>
    </DialogContent>

    <DialogActions>
        <Button onClick={() => setDialogOpen(false)}>
        Cancel
        </Button>

        <Button
        variant="contained"
        onClick={handleSubmit}
        >
        Create
        </Button>
    </DialogActions>
    </Dialog>
</Box>
);
}