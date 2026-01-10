import {GetProps, Input, InputNumber, Slider as AntSlider, ConfigProvider} from "antd";
import {useEffect, useState} from "react";

type SliderProps = GetProps<typeof AntSlider>

function Slider(props: SliderProps) {

    const {onChange, value, ...otherProps} = props
    const [sliderValue, setSliderValue] = useState<number>(0)
    const [inputValue, setInputValue] = useState(props.value?.toString());

    useEffect(() => {
        setSliderValue(value as any)
    }, [value])

    return (
        <ConfigProvider
            theme={{
                components: {
                    Slider: {
                        railBg: '#1a1a1d',
                        railHoverBg: '#222226',
                        trackBg: '#d4a852',
                        trackHoverBg: '#e8c780',
                        handleColor: '#d4a852',
                        handleActiveColor: '#e8c780',
                        dotActiveBorderColor: '#d4a852',
                        colorPrimaryBorderHover: '#d4a852',
                    },
                    Input: {
                        colorBgContainer: '#1a1a1d',
                        colorBorder: 'rgba(255, 255, 255, 0.08)',
                        colorText: '#f0f0f2',
                        colorTextPlaceholder: '#6a6a72',
                        activeBorderColor: '#d4a852',
                        hoverBorderColor: 'rgba(212, 168, 82, 0.3)',
                    }
                }
            }}
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
                            background: '#d4a852',
                        },
                        tracks: {
                            background: '#d4a852',
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
                        background: '#1a1a1d',
                        borderColor: 'rgba(255, 255, 255, 0.08)',
                        color: '#f0f0f2'
                    }}
                />
            </div>
        </ConfigProvider>
    )
}

export default Slider
