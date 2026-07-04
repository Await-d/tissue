import React from "react";
import { useThemeColors } from "../../hooks/useThemeColors";

interface SelectorItem {
    name: string
    value: string
}

interface SelectorProps extends React.ComponentProps<any> {
    items: SelectorItem[]
    value?: string
    onChange?: (value: string) => void
}

function Selector(props: SelectorProps) {

    const {items, value, onChange, ...others} = props
    const colors = useThemeColors()

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
                    background: isSelected ? colors.goldPrimary : colors.bgContainer,
                    color: isSelected ? colors.bgBase : colors.textSecondary,
                    border: `1px solid ${isSelected ? colors.goldPrimary : colors.borderPrimary}`,
                    fontWeight: isSelected ? 600 : 400,
                    boxShadow: isSelected ? `0 0 16px ${colors.rgba('gold', 0.3)}` : 'none'
                }}
                onMouseEnter={(e) => {
                    if (!isSelected) {
                        e.currentTarget.style.background = colors.bgSpotlight
                        e.currentTarget.style.color = colors.textPrimary
                        e.currentTarget.style.borderColor = colors.rgba('gold', 0.3)
                    }
                }}
                onMouseLeave={(e) => {
                    if (!isSelected) {
                        e.currentTarget.style.background = colors.bgContainer
                        e.currentTarget.style.color = colors.textSecondary
                        e.currentTarget.style.borderColor = colors.borderPrimary
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
