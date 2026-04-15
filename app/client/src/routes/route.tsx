
import { createBrowserRouter } from "react-router-dom";
import { Chat } from "@pages/Chat";
import About from "@pages/About";
import Documentation from "@pages/Documentation";
import Layout from "@layout/Layout";



export const router = createBrowserRouter([
    {
        path: "/",
        element: <Layout />,
        children : [
            {
                index: true,
                element: <Chat />
            },
            {
                path: "/about",
                element: <About />
            },
            {
                path: "/documentation",
                element: <Documentation />
            }
        ]
    }
])
