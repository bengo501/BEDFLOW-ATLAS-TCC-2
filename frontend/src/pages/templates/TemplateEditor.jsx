import { useState, useEffect, useRef } from 'react'
import { useLanguage } from '../context/LanguageContext'
import ThemeIcon from './ThemeIcon'
import BackendConnectionError from './BackendConnectionError'
import '../styles/TemplateEditor.css'
import {
  getBedTemplateDefault,
  saveTemplate,
  updateTemplate,
  getTemplate,
  deleteTemplate,
  listTemplates,
} from '../services/api'

function IconCopy({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  )
}

function IconDownload({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function IconRefresh({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M23 4v6h-6" />
      <path d="M1 20v-6h6" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  )
}

function IconImport({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  )
}

function TemplateEditor({ initialEdit = null, onEditConsumed }) {
  const { language, t } = useLanguage()
  const pt = language === 'pt'
  const fileInputRef = useRef(null)
  const [bedContent, setBedContent] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingName, setEditingName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [savedTemplates, setSavedTemplates] = useState([])
  const [showTemplateManager, setShowTemplateManager] = useState(false)
  const [connectionError, setConnectionError] = useState(null)

  useEffect(() => {
    if (initialEdit?.content == null) return
    setBedContent(initialEdit.content)
    setEditingId(initialEdit.id || null)
    setEditingName(initialEdit.name || '')
    onEditConsumed?.()
  }, [initialEdit, onEditConsumed])

  useEffect(() => {
    setConnectionError(null)
    loadSavedTemplates()
    if (initialEdit?.content == null) {
      loadDefaultTemplate()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadDefaultTemplate = async () => {
    try {
      setIsLoading(true)
      const data = await getBedTemplateDefault()
      setBedContent(data.content)
      setEditingId(null)
      setEditingName('')
    } catch (error) {
      console.error('erro ao carregar template padrão:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setIsLoading(false)
    }
  }

  const loadSavedTemplates = async () => {
    try {
      const data = await listTemplates({ page: 1, limit: 100 })
      setSavedTemplates(Array.isArray(data) ? data : data.items || data.templates || [])
    } catch (error) {
      console.error('erro ao carregar templates salvos:', error)
    }
  }

  const handleReload = async () => {
    setConnectionError(null)
    await loadDefaultTemplate()
  }

  const handleImportFile = (event) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setBedContent(e.target.result)
        setEditingId(null)
        setEditingName('')
      }
      reader.readAsText(file)
    }
    event.target.value = ''
  }

  const handleCopyContent = () => {
    navigator.clipboard.writeText(bedContent)
    alert(pt ? 'conteúdo copiado para a área de transferência!' : 'content copied to clipboard!')
  }

  const handleDownloadFile = () => {
    const blob = new Blob([bedContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = editingName ? `${editingName}.bed` : 'template.bed'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSaveTemplate = async () => {
    setConnectionError(null)
    setIsSaving(true)
    try {
      if (editingId) {
        const name =
          editingName.trim() ||
          window.prompt(pt ? 'nome do template:' : 'template name:', editingName) ||
          ''
        if (!name.trim()) return
        await updateTemplate(editingId, {
          name: name.trim(),
          content: bedContent,
          source: 'editor',
        })
        setEditingName(name.trim())
        alert(pt ? 'template atualizado com sucesso!' : 'template updated successfully!')
      } else {
        const templateName = window.prompt(pt ? 'nome do template:' : 'template name:')
        if (!templateName?.trim()) return
        const created = await saveTemplate({
          name: templateName.trim(),
          content: bedContent,
        })
        if (created?.id) {
          setEditingId(created.id)
          setEditingName(created.name || templateName.trim())
        }
        alert(pt ? 'template salvo com sucesso!' : 'template saved successfully!')
      }
      loadSavedTemplates()
    } catch (error) {
      console.error('erro ao salvar template:', error)
      setConnectionError(t('backendConnectionError'))
    } finally {
      setIsSaving(false)
    }
  }

  const handleLoadTemplate = async (templateId) => {
    try {
      setConnectionError(null)
      const data = await getTemplate(templateId)
      setBedContent(data.content)
      setEditingId(data.id)
      setEditingName(data.name)
      setShowTemplateManager(false)
    } catch (error) {
      console.error('erro ao carregar template:', error)
      setConnectionError(t('backendConnectionError'))
    }
  }

  const handleDeleteTemplate = async (templateId) => {
    if (confirm(pt ? 'tem certeza que deseja excluir este template?' : 'delete this template?')) {
      try {
        setConnectionError(null)
        await deleteTemplate(templateId)
        alert(pt ? 'template excluído com sucesso!' : 'template deleted successfully!')
        if (editingId === templateId) {
          setEditingId(null)
          setEditingName('')
        }
        loadSavedTemplates()
      } catch (error) {
        console.error('erro ao excluir template:', error)
        setConnectionError(t('backendConnectionError'))
      }
    }
  }

  return (
    <div className="template-editor-container">
      <div className="template-editor-header">
        <div className="template-editor-title-row">
          <ThemeIcon
            light="textEditorLight.png"
            dark="textEditor.png"
            alt=""
            className="template-editor-title-icon"
            location="page"
          />
          <h2>{pt ? 'Templates' : 'Templates'}</h2>
        </div>
      </div>

      {connectionError && <BackendConnectionError message={connectionError} />}

      <div className="template-editor-content">
        <div className="content-header">
          <h3>{pt ? 'Conteúdo do arquivo .bed' : '.bed file contents'}</h3>
          <div className="content-actions">
            <button
              type="button"
              className="template-inline-btn"
              onClick={() => void handleReload()}
              disabled={isLoading}
            >
              <IconRefresh className="template-toolbar-svg" />
              {pt ? 'recarregar' : 'reload'}
            </button>
            <button
              type="button"
              className="template-inline-btn"
              onClick={() => fileInputRef.current?.click()}
            >
              <IconImport className="template-toolbar-svg" />
              {pt ? 'importar' : 'import'}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".bed"
              onChange={handleImportFile}
              className="template-file-input-hidden"
              aria-hidden
              tabIndex={-1}
            />
            <button type="button" className="btn-copy" onClick={handleCopyContent}>
              <IconCopy className="template-toolbar-svg" />
              {pt ? 'Copiar' : 'Copy'}
            </button>
            <button type="button" className="btn-download" onClick={handleDownloadFile}>
              <IconDownload className="template-toolbar-svg" />
              {pt ? 'Baixar' : 'Download'}
            </button>
            <button
              type="button"
              className="btn-save-template"
              onClick={() => void handleSaveTemplate()}
              disabled={isSaving || !bedContent.trim()}
            >
              {isSaving ? '…' : pt ? 'Salvar' : 'Save'}
            </button>
          </div>
        </div>

        {editingId ? (
          <p className="template-editing-banner">
            {pt ? 'a editar' : 'editing'}: <strong>{editingName || editingId}</strong>
          </p>
        ) : null}

        <div className="bed-editor">
          <textarea
            value={bedContent}
            onChange={(e) => setBedContent(e.target.value)}
            placeholder={pt ? 'Conteúdo do arquivo .bed…' : '.bed file contents…'}
            className="bed-textarea"
          />
        </div>
      </div>

      {showTemplateManager && (
        <div className="template-manager-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{pt ? 'gerenciar templates' : 'manage templates'}</h3>
              <button className="btn-close" onClick={() => setShowTemplateManager(false)}>
                ×
              </button>
            </div>
            <div className="modal-body">
              {savedTemplates.length === 0 ? (
                <p className="no-templates">{pt ? 'nenhum template salvo' : 'no saved templates'}</p>
              ) : (
                <div className="template-list">
                  {savedTemplates.map((template) => (
                    <div key={template.id} className="template-item">
                      <div className="template-info">
                        <h4>{template.name}</h4>
                        <p>
                          {pt ? 'criado em' : 'created'}:{' '}
                          {new Date(template.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="template-actions">
                        <button className="btn-load" onClick={() => handleLoadTemplate(template.id)}>
                          {pt ? 'carregar' : 'load'}
                        </button>
                        <button className="btn-delete" onClick={() => handleDeleteTemplate(template.id)}>
                          {pt ? 'excluir' : 'delete'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TemplateEditor
