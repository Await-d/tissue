import { ComponentProps, forwardRef } from "react";
import Styles from "./index.module.css";
import { useSelector } from "react-redux";
import { RootState } from "../../models";


const IconButton = forwardRef<HTMLSpanElement, ComponentProps<any>>((props, ref) => {

    const { children, ...otherProps } = props
    const currentTheme = useSelector((state: RootState) => state.app?.themeMode)


    return (
        <span ref={ref} {...otherProps}>
            <span
                className={[Styles.container, currentTheme === 'dark' ? Styles.triggerDark : Styles.triggerLight].join(" ")}>
                {children}
            </span>
        </span>
    )
})

export default IconButton
