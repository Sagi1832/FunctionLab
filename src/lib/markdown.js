export const renderMarkdown = (htmlString) => ({
  // TODO: sanitize markdown HTML before rendering
  __html: htmlString,
});

export default renderMarkdown;
