#include <Qt>
#include <QApplication>
#include <QPlainTextEdit>
#include <QSyntaxHighlighter>
#include <QTextDocument>

class SyntaxHighlighter : public QSyntaxHighlighter
{
public:
    SyntaxHighlighter(QTextDocument* document):
        QSyntaxHighlighter(document)
    {}
    
    void highlightBlock(const QString &text)
    {
        if (currentBlock().next().isValid())
            rehighlightBlock(currentBlock().next());
    }
};

int main(int argc, char** argv)
{
    QApplication app (argc, argv);

    QPlainTextEdit pte;
    pte.setPlainText("\n");
    SyntaxHighlighter hl(pte.document());
    pte.show();
    return app.exec();
}
