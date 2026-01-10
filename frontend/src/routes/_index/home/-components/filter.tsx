import React, {useEffect, useState} from "react";
import {Col, GetProp, Row, theme} from "antd";

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
                    color: '#d4a852',
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
                background: 'rgba(26, 26, 29, 0.85)',
                backdropFilter: 'blur(20px) saturate(180%)',
                WebkitBackdropFilter: 'blur(20px) saturate(180%)',
                padding: '20px',
                borderRadius: '14px',
                marginBottom: '20px',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
                transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(212, 168, 82, 0.2)';
                e.currentTarget.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5), 0 0 20px rgba(212, 168, 82, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.05)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05)';
            }}
        >
            <Row {...others} gutter={[12, 12]}>
                {fields.map(field => renderFields(field))}
            </Row>
        </div>
    )
}

export default Filter;
