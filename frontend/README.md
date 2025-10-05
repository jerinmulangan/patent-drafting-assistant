# Patent NLP Frontend

A modern, responsive React frontend for the Patent NLP search and analysis platform. Built with TypeScript, Tailwind CSS, and React Router.

## Features

### 🔍 Advanced Search Interface
- **Multiple Search Modes**: TF-IDF, Semantic, Hybrid, and Hybrid Advanced
- **Advanced Options**: Customizable parameters for fine-tuned control
- **Real-time Search Stats**: Performance metrics and result counts
- **Responsive Design**: Optimized for desktop, tablet, and mobile

### 📊 Search Mode Comparison
- **Side-by-side Comparison**: Compare all search algorithms simultaneously
- **Performance Metrics**: Search time and result count comparisons
- **Visual Results**: Easy-to-read comparison cards

### 📦 Batch Search
- **Multiple Query Processing**: Search up to 50 queries at once
- **File Upload Support**: Upload query lists from text files
- **Export Results**: Download search results as JSON
- **Progress Tracking**: Real-time batch processing status

### 📈 Analytics Dashboard
- **Query Log Analysis**: Insights into search patterns
- **Usage Statistics**: Mode usage distribution and performance metrics
- **Common Queries**: Most frequently searched terms
- **Visual Charts**: Interactive data visualization

### 🎨 Modern UI/UX
- **Dark Mode Support**: Toggle between light and dark themes
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Loading States**: Skeleton components and spinners
- **Error Handling**: Comprehensive error boundaries and user feedback

### 📝 Draft Assistant
- **AI-Powered Drafting**: Generate patent application skeletons
- **Rich Text Interface**: Markdown-style formatting
- **Template System**: Structured patent document generation

## Technology Stack

- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Lucide React**: Beautiful icon library
- **Axios**: HTTP client for API communication

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Textarea.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Alert.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   └── Spinner.tsx
│   │   ├── SearchInterface.tsx # Main search component
│   │   ├── SearchResults.tsx   # Results display
│   │   ├── CompareModes.tsx    # Mode comparison
│   │   ├── BatchSearch.tsx     # Batch processing
│   │   ├── LogAnalysis.tsx     # Analytics dashboard
│   │   ├── DraftAssistant.tsx  # Patent drafting
│   │   ├── Navbar.tsx          # Navigation
│   │   ├── About.tsx           # About page
│   │   └── ThemeToggle.tsx     # Dark mode toggle
│   ├── contexts/
│   │   └── ThemeContext.tsx    # Theme management
│   ├── services/
│   │   └── api.ts              # API client
│   ├── utils/
│   │   └── cn.ts               # Class name utility
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # Global styles
│   ├── index.tsx               # App entry point
│   └── index.css               # Base styles
├── public/
│   └── index.html              # HTML template
├── package.json                # Dependencies
├── tailwind.config.js          # Tailwind configuration
└── tsconfig.json               # TypeScript configuration
```

## Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

## API Integration

The frontend integrates with the Patent NLP backend API through the following endpoints:

- `POST /api/v1/search`: Single search query
- `POST /api/v1/batch_search`: Batch search processing
- `POST /api/v1/compare_modes`: Search mode comparison
- `POST /api/v1/summarize`: Document summarization
- `GET /api/v1/logs/analyze`: Query log analysis
- `GET /api/v1/health`: Health check

## Features in Detail

### Search Interface
- **Query Input**: Large, accessible search input with placeholder examples
- **Mode Selection**: Dropdown with descriptive mode names
- **Advanced Options**: Collapsible section with:
  - Alpha parameter for hybrid mode
  - Custom weights for hybrid-advanced mode
  - Boolean toggles for features
- **Search Statistics**: Real-time performance metrics

### Search Results
- **Enhanced Display**: Improved card layout with better typography
- **Score Visualization**: Percentage-based relevance scores
- **Metadata Display**: Document type, publication date, and ID
- **Summary Generation**: AI-powered document summarization
- **Expandable Content**: Collapsible summary sections

### Batch Search
- **Query Management**: Textarea for multiple queries (one per line)
- **File Upload**: Support for .txt and .csv files
- **Progress Tracking**: Real-time batch processing status
- **Result Export**: JSON download functionality
- **Summary Statistics**: Batch-level performance metrics

### Analytics Dashboard
- **Usage Overview**: Total queries, unique queries, average scores
- **Mode Distribution**: Visual breakdown of search mode usage
- **Top Queries**: Most frequently searched terms
- **Performance Metrics**: Search time and result statistics

### Dark Mode
- **Theme Toggle**: Easy switching between light and dark themes
- **Persistent Storage**: Theme preference saved in localStorage
- **Comprehensive Support**: All components support dark mode
- **Smooth Transitions**: Animated theme switching

## Responsive Design

The frontend is built with a mobile-first approach:

- **Mobile (< 640px)**: Single column layout, stacked components
- **Tablet (640px - 1024px)**: Two-column grids, optimized spacing
- **Desktop (> 1024px)**: Multi-column layouts, full feature set

## Performance Optimizations

- **Code Splitting**: Route-based code splitting with React.lazy
- **Memoization**: React.memo for expensive components
- **Bundle Optimization**: Tree shaking and dead code elimination
- **Image Optimization**: Optimized assets and lazy loading

## Accessibility

- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and roles
- **Color Contrast**: WCAG AA compliant color schemes
- **Focus Management**: Visible focus indicators

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

