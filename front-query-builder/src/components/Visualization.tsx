import React, { useState, useEffect, useMemo } from 'react';
import { useQueryStore } from '../store/useQueryStore';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { FaChartBar, FaChartLine, FaSync, FaChartPie } from 'react-icons/fa';
import './Visualization.css';
import { COLORS } from '../config/chartConstants';
import { useChartFormatters } from '../hooks/useChartFormatters';

const ChartTitle = ({ response, isLoading, error }: any) => {
  let chartTitle = 'Visualização';
  let chartSubtitle = 'Gere uma query ou pergunte à IA para começar';

  if (isLoading) {
    chartTitle = 'Carregando...';
    chartSubtitle = 'Aguarde enquanto buscamos seus dados';
  } else if (error) {
    chartTitle = 'Erro na Consulta';
    chartSubtitle = 'Não foi possível gerar a visualização';
  } else if (response && response.data.length > 0) {
    const firstRow = response.data[0];
    const dimensionKeys = Object.keys(firstRow.dimensions);
    const metricKeys = Object.keys(firstRow.metrics);
    const dimensionKey = dimensionKeys[0] || 'dimensão';
    const friendlyMetric = metricKeys.join(', ').replace(/_/g, ' ');
    const friendlyDimension = dimensionKey.replace(/_/g, ' ');
    chartTitle = friendlyMetric;
    chartSubtitle = `Visualização por ${friendlyDimension}`;
  }

  return (
    <div className="visualization-title">
            <h3>{chartTitle}</h3>      <span>{chartSubtitle}</span>   {' '}
    </div>
  );
};

const GroupedBarChart = React.memo(
  ({ data, dimKey, metKeys, formatters }: any) => {
    return (
      <ResponsiveContainer width="100%" height={400}>
               {' '}
        <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                   {' '}
          <XAxis
            dataKey={dimKey}
            axisLine={false}
            tickLine={false}
            tickFormatter={formatters.xAxis}
          />
                   {' '}
          <YAxis
            axisLine={false}
            tickLine={false}
            tickFormatter={formatters.yAxis}
          />
                    <Tooltip formatter={formatters.tooltip} />
                    <Legend />         {' '}
          {metKeys.map((key: string, index: number) => (
            <Bar
              key={key}
              dataKey={key}
              fill={COLORS[index % COLORS.length]}
              name={key.replace(/_/g, ' ')}
              radius={[4, 4, 0, 0]}
            />
          ))}
                 {' '}
        </BarChart>
             {' '}
      </ResponsiveContainer>
    );
  },
);

const SimpleLineChart = React.memo(
  ({ data, dimKey, metKey, formatters }: any) => {
    return (
      <ResponsiveContainer width="100%" height={400}>
               {' '}
        <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                   {' '}
          <XAxis
            dataKey={dimKey}
            axisLine={false}
            tickLine={false}
            tickFormatter={formatters.xAxis}
          />
                   {' '}
          <YAxis
            axisLine={false}
            tickLine={false}
            tickFormatter={formatters.yAxis}
          />
                    <Tooltip formatter={formatters.tooltip} />
                    <Legend />
                   {' '}
          <Line
            type="monotone"
            dataKey={metKey}
            stroke="#667EEA"
            name={metKey.replace(/_/g, ' ')}
            strokeWidth={2}
          />
                 {' '}
        </LineChart>
             {' '}
      </ResponsiveContainer>
    );
  },
);

const SimplePieChart = React.memo(
  ({ data, dimKey, metKey, formatters }: any) => {
    const pieData = useMemo(
      () =>
        data.map((item: any) => ({
          name: formatters.xAxis(item[dimKey]),
          value: parseFloat(item[metKey]),
        })),
      [data, dimKey, metKey, formatters],
    );

    const renderCustomLabel = (props: any) => {
      const [formattedValue] = formatters.tooltip(props.value, metKey);
      return formattedValue;
    };

    return (
      <ResponsiveContainer width="100%" height={400}>
               {' '}
        <PieChart>
                   {' '}
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={150}
            fill="#8884d8"
            labelLine={true}
            label={renderCustomLabel}
          >
                       {' '}
            {pieData.map((_entry: any, index: number) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
                     {' '}
          </Pie>
                   {' '}
          <Tooltip
            formatter={(value: any) => formatters.tooltip(value, metKey)}
          />
                    <Legend />       {' '}
        </PieChart>
             {' '}
      </ResponsiveContainer>
    );
  },
);

const MultiLineChart = React.memo(
  ({ data, dimKey, metKeys, formatters }: any) => {
    return (
      <ResponsiveContainer width="100%" height={400}>
               {' '}
        <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                   {' '}
          <XAxis
            dataKey={dimKey}
            axisLine={false}
            tickLine={false}
            tickFormatter={formatters.xAxis}
          />
                   {' '}
          <YAxis
            axisLine={false}
            tickLine={false}
            tickFormatter={formatters.yAxis}
          />
                    <Tooltip formatter={formatters.tooltip} />
                    <Legend />         {' '}
          {metKeys.map((key: string, index: number) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={COLORS[index % COLORS.length]}
              name={key.replace(/_/g, ' ')}
              strokeWidth={2}
            />
          ))}
                 {' '}
        </LineChart>
             {' '}
      </ResponsiveContainer>
    );
  },
);

const BiaxialLineChart = React.memo(
  ({ data, dimKey, metKeys, formatters }: any) => {
    if (metKeys.length < 2) {
      return (
        <SimpleLineChart
          data={data}
          dimKey={dimKey}
          metKey={metKeys[0]}
          formatters={formatters}
        />
      );
    }
    return (
      <ResponsiveContainer width="100%" height={400}>
               {' '}
        <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e0e7ff" />
                    <XAxis dataKey={dimKey} tickFormatter={formatters.xAxis} />
                   {' '}
          <YAxis
            yAxisId="left"
            stroke={COLORS[0]}
            tickFormatter={formatters.yAxis}
          />
                   {' '}
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke={COLORS[1]}
            tickFormatter={formatters.yAxis}
          />
                    <Tooltip formatter={formatters.tooltip} />
                    <Legend />
                   {' '}
          <Line
            yAxisId="left"
            type="monotone"
            dataKey={metKeys[0]}
            stroke={COLORS[0]}
            name={metKeys[0].replace(/_/g, ' ')}
          />
                   {' '}
          <Line
            yAxisId="right"
            type="monotone"
            dataKey={metKeys[1]}
            stroke={COLORS[1]}
            name={metKeys[1].replace(/_/g, ' ')}
          />
                 {' '}
        </LineChart>
             {' '}
      </ResponsiveContainer>
    );
  },
);

const TableView = React.memo(({ data, dimKeys, metKeys, formatters }: any) => {
  const allKeys = [...dimKeys, ...metKeys];
  return (
    <div className="viz-table-container">
             {' '}
      <table>
                 {' '}
        <thead>
                     {' '}
          <tr>
                         {' '}
            {allKeys.map((k: string) => (
              <th key={k}>{k.replace(/_/g, ' ')}</th>
            ))}
                       {' '}
          </tr>
                   {' '}
        </thead>
                 {' '}
        <tbody>
                     {' '}
          {data.map((row: any, i: number) => (
            <tr key={i}>
                             {' '}
              {allKeys.map((key: string) => (
                <td key={`${i}-${key}`}>{formatters.table(row[key], key)}</td>
              ))}
                           {' '}
            </tr>
          ))}
                   {' '}
        </tbody>
               {' '}
      </table>
           {' '}
    </div>
  );
});

const VizMessage = ({ message, isError = false }: any) => (
  <div className="viz-message-overlay">
        <p style={{ color: isError ? '#d9534f' : 'inherit' }}>{message}</p>
     {' '}
  </div>
);

export function Visualization() {
  const { response, isLoading, error } = useQueryStore();
  const [activeChart, setActiveChart] = useState('BarChart');

  useEffect(() => {
    if (response?.chart_suggestion) {
      setActiveChart(response.chart_suggestion);
    } else if (!response) {
      setActiveChart('BarChart');
    }
  }, [response]);

  const chartData = useMemo(() => {
    if (!response || response.data.length === 0) return null;

    const flattenedData = response.data.map((row) => ({
      ...row.dimensions,
      ...row.metrics,
    }));
    const firstRow = response.data[0];
    const dimensionKeys = Object.keys(firstRow.dimensions);
    const metricKeys = Object.keys(firstRow.metrics);

    return {
      flattenedData,
      dimensionKeys,
      metricKeys,
      dimensionKey: dimensionKeys[0],
      metricKey: metricKeys[0],
    };
  }, [response]);

  const formatters = useChartFormatters(
    chartData?.dimensionKeys || [],
    chartData?.metricKeys || [],
  );

  const renderChartContent = () => {
    if (isLoading) {
      return <VizMessage message="Carregando..." />;
    }
    if (error) {
      return <VizMessage message={error} isError />;
    }
    if (!chartData) {
      return <VizMessage message="Nenhum dado para exibir." />;
    }

    const {
      flattenedData,
      dimensionKeys,
      metricKeys,
      dimensionKey,
      metricKey,
    } = chartData;

    const chartProps = {
      data: flattenedData,
      dimKey: dimensionKey,
      metKeys: metricKeys,
      metKey: metricKey,
      dimKeys: dimensionKeys,
      formatters,
    };

    switch (activeChart) {
      case 'LineChart':
        return metricKeys.length > 1 ? (
          <MultiLineChart {...chartProps} />
        ) : (
          <SimpleLineChart {...chartProps} />
        );
      case 'MultiLineChart':
        return <MultiLineChart {...chartProps} />;
      case 'BiaxialLineChart':
        return <BiaxialLineChart {...chartProps} />;
      case 'PieChart':
        return <SimplePieChart {...chartProps} />;
      case 'Table':
        return <TableView {...chartProps} />;
      case 'BarChart':
      case 'GroupedBarChart':
      default:
        return <GroupedBarChart {...chartProps} />;
    }
  };

  return (
    <div className="visualization-area">
           {' '}
      <div className="visualization-container">
               {' '}
        <div className="visualization-header">
                   {' '}
          <ChartTitle response={response} isLoading={isLoading} error={error} />
                   {' '}
          <div className="visualization-controls">
                       {' '}
            <button
              className={`viz-control-button ${
                activeChart.includes('Line') ? 'active' : ''
              }`}
              onClick={() => setActiveChart('LineChart')}
            >
                            <FaChartLine />           {' '}
            </button>
                       {' '}
            <button
              className={`viz-control-button ${
                activeChart.includes('Bar') ? 'active' : ''
              }`}
              onClick={() => setActiveChart('BarChart')}
            >
                          <FaChartBar />           {' '}
            </button>
                   {' '}
            <button
              className={`viz-control-button ${
                activeChart === 'PieChart' ? 'active' : ''
              }`}
              onClick={() => setActiveChart('PieChart')}
            >
                        <FaChartPie />     {' '}
            </button>
             {' '}
            <button className="viz-control-button">
                    <FaSync /> {' '}
            </button>
             {' '}
          </div>
           {' '}
        </div>
            <div className="visualization-body">{renderChartContent()}</div>
         {' '}
      </div>
       {' '}
    </div>
  );
}
