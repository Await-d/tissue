import React, { useState } from "react";
import { Col, Row } from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";

export interface FilterField {
    dataIndex: string,
    label: string,
    component: React.ReactElement
    span?: { xs?: number, md?: number, lg?: number }
}

interface FilterProps extends React.ComponentProps<any> {
    fields: FilterField[]
    initialValues: object
    onChange: (values: object, filed?: string) => void
    compact?: boolean
}

function Filter(props: FilterProps) {

    const {fields, initialValues = {}, onChange, compact = false, ...others} = props
    const [values, setValues] = useState<any>(initialValues)
    const colors = useThemeColors();
    const fieldMinHeight = compact ? 38 : 48
    const labelMinWidth = compact ? '3em' : '3.5em'
    const labelFontSize = compact ? '12px' : '13px'

    function renderFields(field: FilterField) {

        const child = React.cloneElement(field.component, {
            value: values[field.dataIndex],
            onChange: (value: object) => {
                const newValues = {...values, [field.dataIndex]: value}
                setValues(newValues)
                onChange?.(newValues, field.dataIndex)
            }
        })

        return (
            <Col key={field.dataIndex} {...field.span} className={'flex items-center'} style={{ minHeight: fieldMinHeight }}>
                <div className={compact ? 'mr-2' : 'mr-3'} style={{
                    fontWeight: 600,
                    color: colors.textGold,
                    minWidth: labelMinWidth,
                    fontSize: labelFontSize,
                    letterSpacing: '0.02em',
                    textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                }}>{field.label}</div>
                <div className={'flex-1'}>
                    {child}
                </div>
            </Col>
        )
    }

    return (
        <div
            className="tissue-glass tissue-animate-in"
            style={{
                background: colors.rgba('black', 0.15),
                backdropFilter: 'blur(20px) saturate(180%)',
                WebkitBackdropFilter: 'blur(20px) saturate(180%)',
                padding: compact ? '12px' : '20px',
                borderRadius: compact ? '12px' : '14px',
                marginBottom: compact ? '8px' : '20px',
                border: `1px solid ${colors.borderPrimary}`,
                boxShadow: `${colors.shadowMd}, inset 0 1px 0 ${colors.rgba('white', 0.05)}`,
                transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
            }}
        >
            <Row {...others} gutter={compact ? [8, 8] : [12, 12]}>
                {fields.map(field => renderFields(field))}
            </Row>
        </div>
    )
}

export default Filter;
