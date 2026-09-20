import {useEffect, useState} from "react";

function useVisibility() {

    const [visible, setVisible] = useState<boolean>(false)

    function handleVisibilityChange() {
        if (document.visibilityState === 'visible') {
            handleForeground();
        } else {
            handleBackground();
        }
    }

    function handleForeground() {
        console.log('App 进入前台');
        setVisible(true);
    }

    function handleBackground() {
        console.log('App 退到后台');
        setVisible(false)
    }


    useEffect(() => {

        window.addEventListener('blur', handleBackground)
        window.addEventListener('focus', handleForeground)

        document.addEventListener("visibilitychange", handleVisibilityChange)

        return () => {
            window.removeEventListener('blur', handleBackground)
            window.removeEventListener('focus', handleForeground)
            document.removeEventListener("visibilitychange", handleVisibilityChange)
        }
        // 处理器只调用 setState/console，无外部状态依赖；监听器只需在挂载时注册一次，[] 为刻意选择
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    return visible
}

export default useVisibility
