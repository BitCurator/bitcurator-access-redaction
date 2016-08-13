#ifndef REDACTWINDOW_H
#define REDACTWINDOW_H

#include <QMainWindow>

namespace Ui {
class RedactWindow;
}

class RedactWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit RedactWindow(QWidget *parent = 0);
    ~RedactWindow();

private:
    Ui::RedactWindow *ui;
};

#endif // REDACTWINDOW_H
