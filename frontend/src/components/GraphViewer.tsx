// frontend/src/components/GraphViewer.tsx
import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface Props {
  points: number[][]
  tour?: number[]
  width?: number
  height?: number
}

export default function GraphViewer({ points, tour, width = 400, height = 300 }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || points.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const pad = 30
    const xs = points.map(p => p[0])
    const ys = points.map(p => p[1])
    const xScale = d3.scaleLinear().domain([Math.min(...xs), Math.max(...xs)]).range([pad, width - pad])
    const yScale = d3.scaleLinear().domain([Math.min(...ys), Math.max(...ys)]).range([height - pad, pad])

    // Draw tour edges
    if (tour && tour.length > 0) {
      const line = d3.line<number>()
        .x(i => xScale(points[i][0]))
        .y(i => yScale(points[i][1]))
      svg.append('path')
        .datum([...tour, tour[0]])
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', '#6ee7b7')
        .attr('stroke-width', 2)
        .attr('opacity', 0.8)
    }

    // Draw nodes
    svg.selectAll('circle')
      .data(points)
      .enter()
      .append('circle')
      .attr('cx', d => xScale(d[0]))
      .attr('cy', d => yScale(d[1]))
      .attr('r', 4)
      .attr('fill', '#6ee7b7')

    // Draw node labels
    svg.selectAll('text')
      .data(points)
      .enter()
      .append('text')
      .attr('x', d => xScale(d[0]) + 6)
      .attr('y', d => yScale(d[1]) - 6)
      .attr('fill', '#475569')
      .attr('font-size', '9px')
      .attr('font-family', 'JetBrains Mono, monospace')
      .text((_, i) => i)
  }, [points, tour, width, height])

  return (
    <div className="panel">
      <div className="panel-header">Instance Viewer</div>
      <svg ref={svgRef} width={width} height={height} style={{ background: 'var(--bg)' }} />
    </div>
  )
}
