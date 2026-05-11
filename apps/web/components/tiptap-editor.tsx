"use client";

import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useEffect } from "react";

type TipTapEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

export function TipTapEditor({ value, onChange }: TipTapEditorProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: value,
    editorProps: {
      attributes: {
        class:
          "min-h-[140px] rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-7 text-ink focus:outline-none"
      }
    },
    onUpdate({ editor: currentEditor }) {
      onChange(currentEditor.getHTML());
    }
  });

  useEffect(() => {
    if (editor && editor.getHTML() !== value) {
      editor.commands.setContent(value, false);
    }
  }, [editor, value]);

  return <EditorContent editor={editor} />;
}

