import { useEffect, useState } from "react";
import { Box } from "@mui/material";

import api from "../../api/client";
import AtmCard from "./AtmCard";


export default function AtmList() {
const [atms, setAtms] = useState([]);

useEffect(() => {
async function fetchAtms() {
    const response = await api.get("/atms");
    setAtms(response.data);
}

fetchAtms();
}, []);

return (
<Box>
    {atms.map((atm) => (
    <AtmCard
        key={atm.id}
        atm={atm}
    />
    ))}
</Box>
);
}