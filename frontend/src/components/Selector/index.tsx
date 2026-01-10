import React from "react";
import {theme} from "antd";

interface SelectorItem {
    name: string
    value: string
}

interface SelectorProps extends React.ComponentProps<any> {
    items: SelectorItem[]
    value?: string
    onChange?: (value: string) => void
}

const {useToken} = theme

function Selector(props: SelectorProps) {

    const {items, value, onChange, ...others} = props
    const {token} = useToken()

    function renderItem(item: SelectorItem) {
        const isSelected = item.value === value
        return (
            <div
                key={item.value}
                className={'mr-2 px-4 py-1 cursor-pointer rounded-md transition-all duration-300'}
                onClick={() => {
                    if (item.value !== props.value) {
                        onChange?.(item.value)
                    }
                }}
                style={{
                    background: isSelected ? '#d4a852' : '#1a1a1d',
                    color: isSelected ? '#0d0d0f' : '#a0a0a8',
                    border: `1px solid ${isSelected ? '#d4a852' : 'rgba(255, 255, 255, 0.08)'}`,
                    fontWeight: isSelected ? 600 : 400,
                    boxShadow: isSelected ? '0 0 16px rgba(212, 168, 82, 0.3)' : 'none'
                }}
                onMouseEnter={(e) => {
                    if (!isSelected) {
                        e.currentTarget.style.background = '#222226'
                        e.currentTarget.style.color = '#f0f0f2'
                        e.currentTarget.style.borderColor = 'rgba(212, 168, 82, 0.3)'
                    }
                }}
                onMouseLeave={(e) => {
                    if (!isSelected) {
                        e.currentTarget.style.background = '#1a1a1d'
                        e.currentTarget.style.color = '#a0a0a8'
                        e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)'
                    }
                }}
            >
                {item.name}
            </div>
        )
    }

    return (
        <div {...others} className={'flex'}>
            {items.map(item => renderItem(item))}
        </div>
    )
}

export default Selector
