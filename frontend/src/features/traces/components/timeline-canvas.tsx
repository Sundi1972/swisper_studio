/**
 * Timeline Canvas Component
 * 
 * D3.js-based waterfall/timeline visualization of trace execution.
 * Displays observations as horizontal bars positioned on a timeline.
 */

import { useEffect, useRef, useState, useImperativeHandle, forwardRef } from 'react';
import { Box } from '@mui/material';
import * as d3 from 'd3';
import type { TimelineData, TimelineNode } from '../types/timeline';

interface TimelineCanvasProps {
  data: TimelineData;
  onNodeClick: (node: TimelineNode) => void;
  onToggleExpand: (nodeId: string) => void;
  selectedNodeId?: string;
}

export interface TimelineCanvasRef {
  zoomIn: () => void;
  zoomOut: () => void;
  fitToScreen: () => void;
}

// Layout constants
const MARGIN = { top: 40, right: 20, bottom: 20, left: 250 };
const ROW_HEIGHT = 32;
const BAR_HEIGHT = 24;
const INDENT_PER_LEVEL = 20;
const MIN_BAR_WIDTH = 2; // Minimum width for very short duration bars

// Zoom constants
const ZOOM_IN_FACTOR = 1.3;
const ZOOM_OUT_FACTOR = 0.7;
const ZOOM_MIN_SCALE = 0.5;
const ZOOM_MAX_SCALE = 5;
const ZOOM_TRANSITION_MS = 300;
const FIT_TRANSITION_MS = 750;

export const TimelineCanvas = forwardRef<TimelineCanvasRef, TimelineCanvasProps>(
  function TimelineCanvas({ data, onNodeClick, onToggleExpand, selectedNodeId }, ref) {
    const svgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    // Zoom behavior ref (persistent across renders)
    const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

  // Responsive sizing with ResizeObserver
  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });

    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  // D3 rendering - re-render when data or dimensions change
  useEffect(() => {
    if (!svgRef.current || dimensions.width === 0) return;

    renderTimeline();
  }, [data, dimensions, selectedNodeId]);

  /**
   * Main D3 rendering function
   */
  function renderTimeline() {
    try {
      const svg = d3.select(svgRef.current!);
      svg.selectAll('*').remove(); // Clear previous render

    const width = dimensions.width;
    const visibleNodes = data.nodes.filter((n) => n.isVisible);
    // Calculate content height (don't constrain to container height)
    const contentHeight = visibleNodes.length * ROW_HEIGHT + MARGIN.top + MARGIN.bottom;

    // Set SVG to content size (allows scrolling when zoomed)
    svg.attr('width', width).attr('height', contentHeight);

    // Create main group for zoom/pan transform
    const g = svg.append('g').attr('class', 'timeline-main');

    // Create X scale (time axis)
    const xScale = d3
      .scaleLinear()
      .domain([0, data.totalDuration])
      .range([MARGIN.left, width - MARGIN.right]);

    // Create time axis at top
    const xAxis = d3
      .axisTop(xScale)
      .ticks(Math.min(10, Math.floor((width - MARGIN.left - MARGIN.right) / 80)))
      .tickFormat((d) => `${(Number(d) / 1000).toFixed(1)}s`);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0, ${MARGIN.top})`)
      .call(xAxis)
      .style('color', '#B0B0B0')  // Lighter for better contrast
      .style('font-size', '11px');

    // Create row groups
    const rows = g
      .selectAll('.timeline-row')
      .data(visibleNodes)
      .enter()
      .append('g')
      .attr('class', 'timeline-row')
      .attr('transform', (_d, i) => `translate(0, ${MARGIN.top + i * ROW_HEIGHT})`);

    // Row background (hover effect)
    rows
      .append('rect')
      .attr('class', 'row-bg')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', ROW_HEIGHT)
      .attr('fill', 'transparent')
      .on('mouseenter', function () {
        d3.select(this).attr('fill', 'rgba(0, 0, 0, 0.03)');
      })
      .on('mouseleave', function () {
        d3.select(this).attr('fill', 'transparent');
      });

    // Expand/collapse icon (for nodes with children)
    rows
      .filter((d) => d.children.length > 0)
      .append('text')
      .attr('class', 'expand-icon')
      .attr('x', (d) => INDENT_PER_LEVEL * d.depth + 5)
      .attr('y', ROW_HEIGHT / 2 + 5)
      .text((d) => (d.isExpanded ? '▼' : '▶'))
      .style('font-size', '10px')
      .style('fill', '#A0A0A0')  // Lighter gray for better visibility
      .style('cursor', 'pointer')
      .on('click', function (_event, d) {
        _event.stopPropagation();
        onToggleExpand(d.id);
      });

    // Node label (left side)
    rows
      .append('text')
      .attr('class', 'node-label')
      .attr('x', (d) => {
        const hasChildren = d.children.length > 0;
        const baseIndent = INDENT_PER_LEVEL * d.depth;
        return baseIndent + (hasChildren ? 20 : 10);
      })
      .attr('y', ROW_HEIGHT / 2 + 5)
      .text((d) => d.name)
      .style('font-size', (d) => (d.depth === 0 ? '14px' : '13px'))
      .style('fill', '#E0E0E0')  // Light gray for better contrast on dark background
      .style('font-weight', (d) => (d.depth === 0 ? 'bold' : 'normal'))
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        onNodeClick(d);
      });

    // Error indicator (⚠️ before label)
    rows
      .filter((d) => d.hasError)
      .append('text')
      .attr('x', (d) => INDENT_PER_LEVEL * d.depth + (d.children.length > 0 ? 20 : 10) - 18)
      .attr('y', ROW_HEIGHT / 2 + 5)
      .text('⚠️')
      .style('font-size', '14px');

    // Timeline bar
    rows
      .append('rect')
      .attr('class', 'timeline-bar')
      .attr('x', (d) => xScale(d.startTime))
      .attr('y', (ROW_HEIGHT - BAR_HEIGHT) / 2)
      .attr('width', (d) => Math.max(MIN_BAR_WIDTH, xScale(d.endTime) - xScale(d.startTime)))
      .attr('height', BAR_HEIGHT)
      .attr('rx', 3)
      .attr('ry', 3)
      .attr('fill', (d) => d.color)
      .attr('opacity', (d) => (d.hasError ? 0.7 : 0.85))
      .attr('stroke', (d) => (d.id === selectedNodeId ? '#000' : d.hasError ? '#d32f2f' : 'none'))
      .attr('stroke-width', (d) => (d.id === selectedNodeId ? 3 : d.hasError ? 2 : 0))
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        onNodeClick(d);
      })
      .on('mouseenter', function () {
        // Highlight on hover
        d3.select(this)
          .attr('opacity', 1)
          .attr('stroke', '#000')
          .attr('stroke-width', 1);
      })
      .on('mouseleave', function (_event, d) {
        // Reset unless selected
        if (d.id !== selectedNodeId) {
          d3.select(this)
            .attr('opacity', d.hasError ? 0.7 : 0.85)
            .attr('stroke', d.hasError ? '#d32f2f' : 'none')
            .attr('stroke-width', d.hasError ? 2 : 0);
        }
      });

    // Duration label (right side of bar)
    rows
      .append('text')
      .attr('class', 'duration-label')
      .attr('x', (d) => xScale(d.endTime) + 8)
      .attr('y', ROW_HEIGHT / 2 + 5)
      .text((d) => {
        const seconds = d.duration / 1000;
        return seconds < 0.01 ? '<0.01s' : `${seconds.toFixed(2)}s`;
      })
      .style('font-size', '11px')
      .style('fill', '#B0B0B0')  // Lighter gray for better contrast
      .style('font-family', 'monospace');

    // Tooltips
    rows.append('title').text((d) => {
      const lines = [
        `${d.name}`,
        `Type: ${d.type}`,
        `Duration: ${(d.duration / 1000).toFixed(3)}s`,
      ];
      
      if (d.totalCost) {
        lines.push(`Cost: CHF ${parseFloat(d.totalCost).toFixed(4)}`);
      }
      
      if (d.totalTokens) {
        lines.push(`Tokens: ${d.totalTokens.toLocaleString()}`);
      }
      
      if (d.model) {
        lines.push(`Model: ${d.model}`);
      }
      
      return lines.join('\n');
    });

      // Setup zoom behavior
      const zoom = d3
        .zoom<SVGSVGElement, unknown>()
        .scaleExtent([ZOOM_MIN_SCALE, ZOOM_MAX_SCALE])
        .on('zoom', (event) => {
          g.attr('transform', event.transform.toString());
        });

      svg.call(zoom);

      // Store zoom behavior for external controls
      zoomBehaviorRef.current = zoom;

      // Auto-fit to screen on initial render
      if (!selectedNodeId) {
        setTimeout(() => fitToScreen(), 100);
      }
    } catch (error) {
      console.error('Timeline rendering failed:', error);
      // Timeline will show empty, but app won't crash
    }
  }

  /**
   * Fit timeline to screen
   * Resets zoom to default 1:1 scale with smooth transition
   */
  function fitToScreen() {
    if (!svgRef.current || !zoomBehaviorRef.current) return;

    const svg = d3.select(svgRef.current);

    // Reset transform with smooth transition
    svg
      .transition()
      .duration(FIT_TRANSITION_MS)
      .call(
        zoomBehaviorRef.current.transform as any,
        d3.zoomIdentity.translate(0, 0).scale(1)
      );
  }

  /**
   * Zoom in by constant factor
   */
  function zoomIn() {
    if (!svgRef.current || !zoomBehaviorRef.current) return;

    const svg = d3.select(svgRef.current);
    svg
      .transition()
      .duration(ZOOM_TRANSITION_MS)
      .call(zoomBehaviorRef.current.scaleBy as any, ZOOM_IN_FACTOR);
  }

  /**
   * Zoom out by constant factor
   */
  function zoomOut() {
    if (!svgRef.current || !zoomBehaviorRef.current) return;

    const svg = d3.select(svgRef.current);
    svg
      .transition()
      .duration(ZOOM_TRANSITION_MS)
      .call(zoomBehaviorRef.current.scaleBy as any, ZOOM_OUT_FACTOR);
  }

  // Expose zoom controls to parent via ref
  useImperativeHandle(ref, () => ({
    zoomIn,
    zoomOut,
    fitToScreen,
  }));

  // Auto-fit on initial render
  useEffect(() => {
    if (dimensions.width > 0 && data.nodes.length > 0) {
      setTimeout(() => fitToScreen(), 100);
    }
  }, [data.nodeCount, dimensions.width]);

  return (
    <Box
      ref={containerRef}
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: 'background.default',
        position: 'relative',
      }}
    >
      <svg
        ref={svgRef}
        style={{
          display: 'block',
          // Let D3 set width/height dynamically, don't constrain
        }}
      />
    </Box>
  );
});

