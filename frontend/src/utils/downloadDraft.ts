/**
 * Utility functions for downloading patent drafts in multiple formats
 */

import { Document, Packer, Paragraph, AlignmentType } from 'docx';

type DownloadFormat = 'txt' | 'pdf' | 'docx';

const getFileName = (format: DownloadFormat): string => {
  const date = new Date().toISOString().split('T')[0];
  const baseFileName = `patent_draft_${date}`;
  
  switch (format) {
    case 'txt':
      return `${baseFileName}.txt`;
    case 'pdf':
      return `${baseFileName}.pdf`;
    case 'docx':
      return `${baseFileName}.docx`;
  }
};

/**
 * Download draft as plain text file
 */
export const downloadAsText = (content: string): void => {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = getFileName('txt');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Download draft as DOCX (Word) file
 */
export const downloadAsDocx = async (content: string): Promise<void> => {
  try {
    // Parse content into paragraphs (split by double newlines or significant breaks)
    const paragraphs = content
      .split(/\n\n+/)
      .filter(p => p.trim().length > 0)
      .map(text => {
        // Check if this looks like a heading (starts with ##, starts with all caps, or is short)
        const isHeading = text.startsWith('##') || 
                         (text.length < 100 && text === text.toUpperCase()) ||
                         /^[A-Z\s]{10,}$/.test(text);
        
        const cleanText = text.replace(/^#+\s*/, '').trim(); // Remove markdown headers
        
        return new Paragraph({
          text: cleanText,
          spacing: { line: 240, after: 200 },
          alignment: AlignmentType.LEFT,
          ...(isHeading && cleanText.length < 100 ? { bold: true } : {})
        });
      });

    const doc = new Document({
      sections: [
        {
          properties: {},
          children: paragraphs
        }
      ]
    });

    const blob = await Packer.toBlob(doc);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = getFileName('docx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Error generating DOCX:', err);
    alert('Failed to generate DOCX file. Using text download instead.');
    downloadAsText(content);
  }
};

/**
 * Download draft as PDF file using jsPDF
 */
export const downloadAsPdf = async (content: string): Promise<void> => {
  try {
    // Dynamic import to avoid bundle size issues
    const { jsPDF } = await import('jspdf');
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const pageHeight = pdf.internal.pageSize.getHeight();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const margin = 10;
    const lineHeight = 7;
    const textWidth = pageWidth - 2 * margin;
    
    // Split content into lines and fit to page
    const lines = content.split('\n');
    let yPosition = margin;

    lines.forEach((line) => {
      // Check if line looks like a heading
      const isHeading = line.startsWith('##') || 
                       /^[A-Z\s]{10,}$/.test(line);
      
      const cleanLine = line.replace(/^#+\s*/, '').trim();
      
      if (!cleanLine) return; // Skip empty lines
      
      // Wrap long lines
      const wrappedLines = pdf.splitTextToSize(cleanLine, textWidth);
      const lineHeightMultiplier = isHeading ? 1.5 : 1;
      const currentLineHeight = lineHeight * lineHeightMultiplier;

      wrappedLines.forEach((wrappedLine: string, wIdx: number) => {
        if (yPosition > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }
        
        pdf.setFontSize(isHeading && wIdx === 0 ? 14 : 11);
        if (isHeading && wIdx === 0) {
          pdf.setFont('helvetica', 'bold');
        } else {
          pdf.setFont('helvetica', 'normal');
        }
        pdf.text(wrappedLine, margin, yPosition);
        yPosition += currentLineHeight;
      });

      // Add extra space after headings
      if (isHeading) {
        yPosition += lineHeight;
      }
    });

    pdf.save(getFileName('pdf'));
  } catch (err) {
    console.error('Error generating PDF:', err);
    alert('Failed to generate PDF file. Using text download instead.');
    downloadAsText(content);
  }
};

/**
 * Main download function that dispatches to the appropriate format handler
 */
export const downloadDraft = async (content: string, format: DownloadFormat): Promise<void> => {
  switch (format) {
    case 'txt':
      downloadAsText(content);
      break;
    case 'docx':
      await downloadAsDocx(content);
      break;
    case 'pdf':
      await downloadAsPdf(content);
      break;
    default:
      downloadAsText(content);
  }
};
