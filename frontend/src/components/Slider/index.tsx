import {GetProps, Input, Slider as AntSlider, ConfigProvider} from "antd";
import {useEffect, useMemo, useState} from "react";
import {useThemeColors} from "../../hooks/useThemeColors";

type SliderProps = GetProps<typeof AntSlider>

function Slider(props: SliderProps) {

    const colors = useThemeColors()
    const {onChange, value, ...otherProps} = props
    const [sliderValue, setSliderValue] = useState<number>(0)
    const [inputValue, setInputValue] = useState(props.value?.toString());

    useEffect(() => {
        setSliderValue(value as any)
    }, [value])

    const themeConfig = useMemo(() => ({
        components: {
            Slider: {
                railBg: colors.bgContainer,
                railHoverBg: colors.bgSpotlight,
                trackBg: colors.goldPrimary,
                trackHoverBg: colors.goldLight,
                handleColor: colors.goldPrimary,
                handleActiveColor: colors.goldLight,
                dotActiveBorderColor: colors.goldPrimary,
                colorPrimaryBorderHover: colors.goldPrimary,
            },
            Input: {
                colorBgContainer: colors.bgContainer,
                colorBorder: colors.borderPrimary,
                colorText: colors.textPrimary,
                colorTextPlaceholder: colors.textTertiary,
                activeBorderColor: colors.goldPrimary,
                hoverBorderColor: colors.borderGold,
            }
        }
    }), [colors])

    return (
        <ConfigProvider
            theme={themeConfig}
        >
            <div className={'flex items-center'}>
                <AntSlider
                    className={'flex-1'}
                    {...otherProps}
                    value={sliderValue as any}
                    onChange={(value: any) => {
                        setSliderValue(value)
                        setInputValue(value)
                    }}
                    onChangeComplete={(value: any) => {
                        setSliderValue(value)
                        setInputValue(value)
                        onChange?.(value)
                    }}
                    styles={{
                        track: {
                            background: colors.goldPrimary,
                        },
                        tracks: {
                            background: colors.goldPrimary,
                        }
                    }}
                />
                <Input
                    value={inputValue}
                    onChange={(event) => {
                        setInputValue(event.target.value)
                        if (!isNaN(Number(event.target.value))) {
                            onChange?.(event.target.value as any)
                        }
                    }}
                    className={'w-12 ml-2'}
                    style={{
                        background: colors.bgContainer,
                        borderColor: colors.borderPrimary,
                        color: colors.textPrimary
                    }}
                />
            </div>
        </ConfigProvider>
    )
}

export default Slider
