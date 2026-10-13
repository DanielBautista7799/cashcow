import { createTheme } from "@mui/material";

const theme = createTheme({
colorSchemes: {
light: {
    palette: {
    primary: { main: "#3F7467" },
    background: {
        default: "#F6F3EC",
        paper: "#FFFFFF",
    },
    text: {
        primary: "#26352F",
        secondary: "#68756F",
    },
    },
},

dark: {
    palette: {
    primary: { main: "#7DB5A6" },
    background: {
        default: "#18201D",
        paper: "#24302B",
    },
    text: {
        primary: "#F3F6F4",
        secondary: "#B8C5C0",
    },
    },
},
},

shape: {
borderRadius: 10,
},
});

export default theme;