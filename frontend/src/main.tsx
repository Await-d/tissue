import React from 'react';
import ReactDOM from 'react-dom/client';
import {Provider, useSelector} from "react-redux";
import {RouterProvider} from "@tanstack/react-router";

import {RootState, store} from "./models";
import {configureRequest} from "./utils/requests";

import './index.css';
import {router} from "./routes.tsx";

// 在应用启动、任何请求发出之前完成请求层依赖注入（token 读取与 401 登出）。
configureRequest({
    getToken: () => store.getState().auth?.userToken,
    onUnauthorized: () => { store.dispatch.auth.logout() }
})

function InnerApp() {
    const {userToken} = useSelector((state: RootState) => state.auth)
    return <RouterProvider router={router} context={{userToken}}/>
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <Provider store={store}>
            <InnerApp/>
        </Provider>
    </React.StrictMode>
)
