import React, {useEffect, useState} from "react";
import {Col, GetProp, Row, theme} from "antd";
import { useThemeColors } from "../../../../hooks/useThemeColors";

const { useToken } = theme;

type ColSpan = GetProp<typeof Col, 'span'>

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
}

function Filter(props: FilterProps) {

    const {fields, initialValues = {}, onChange, ...others} = props
    const [values, setValues] = useState<any>(initialValues)
    const { token } = useToken();
    const colors = useThemeColors();

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
            <Col key={field.dataIndex} {...field.span} className={'flex items-center h-12'}>
                <div className={'mr-3'} style={{
                    fontWeight: 600,
                    color: colors.textGold,
                    minWidth: '3.5em',
                    fontSize: '13px',
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
                padding: '20px',
                borderRadius: '14px',
                marginBottom: '20px',
                border: `1px solid ${colors.borderPrimary}`,
                boxShadow: `${colors.shadowMd}, inset 0 1px 0 ${colors.rgba('white', 0.05)}`,
                transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = colors.borderGold;
                e.currentTarget.style.boxShadow = `0 4px 20px rgba(0, 0, 0, 0.5), 0 0 20px ${colors.rgba('gold', 0.1)}, inset 0 1px 0 ${colors.rgba('white', 0.05)}`;
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = colors.borderPrimary;
                e.currentTarget.style.boxShadow = `${colors.shadowMd}, inset 0 1px 0 ${colors.rgba('white', 0.05)}`;
            }}
        >
            <Row {...others} gutter={[12, 12]}>
                {fields.map(field => renderFields(field))}
            </Row>
        </div>
    )
}

export default Filter;
