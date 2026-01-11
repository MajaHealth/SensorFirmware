// DebugWindow.h
#ifndef DEBUGWINDOW_H
#define DEBUGWINDOW_H

#include <string>
#include <thread>
#include <mutex>
#include <cstring>

#include <FL/Fl.H>
#include <FL/Fl_Window.H>
#include <FL/Fl_Box.H>
#include <FL/Fl_Button.H>

class DebugWindow
{
public:
    DebugWindow(int width, int height, const std::string& title);
    ~DebugWindow();

    // Методи для незалежного оновлення лівого та правого вікна
    void update_data_1(const std::string& value); // Ліве
    void update_data_2(const std::string& value); // Праве

private:
    void gui_thread_function();
    void redraw_widget();
    static void update_callback(void* data);
    static void copy_callback(Fl_Widget* w, void* data);

    Fl_Window* window;
    Fl_Box* value_box_1; // Лівий
    Fl_Box* value_box_2; // Правий
    Fl_Button* copy_button;

    std::thread gui_thread;
    std::mutex value_mutex;

    std::string current_value_1;
    std::string current_value_2;
    std::string window_title;

    bool is_running;
    int _width;
    int _height;
};

inline DebugWindow::DebugWindow(int width, int height, const std::string& title)
    : window(nullptr), value_box_1(nullptr), value_box_2(nullptr),
      current_value_1("LEFT DATA"), current_value_2("RIGHT DATA"),
      window_title(title), is_running(true), _width(width), _height(height)
{
    Fl::lock();
    gui_thread = std::thread(&DebugWindow::gui_thread_function, this);
}

inline DebugWindow::~DebugWindow()
{
    is_running = false;
    Fl::awake();

    if (gui_thread.joinable())
    {
        gui_thread.join();
    }
}

inline void DebugWindow::update_data_1(const std::string& value)
{
    {
        std::lock_guard<std::mutex> lock(value_mutex);
        current_value_1 = value;
    }
    Fl::awake();
}

inline void DebugWindow::update_data_2(const std::string& value)
{
    {
        std::lock_guard<std::mutex> lock(value_mutex);
        current_value_2 = value;
    }
    Fl::awake();
}

inline void DebugWindow::gui_thread_function()
{
    window = new Fl_Window(_width, _height, window_title.c_str());


    int gap = 10;
    int margin = 10;
    int button_h = 40;

    int box_w = (_width - (2 * margin) - gap) / 2;

       int box_h = _height - button_h - (2 * margin);

    value_box_1 = new Fl_Box(margin, margin, box_w, box_h, "NO DATA 1");
    value_box_1->box(FL_DOWN_BOX);
    value_box_1->color(FL_WHITE);
    value_box_1->labelsize(12);
    value_box_1->labelfont(FL_BOLD);
    value_box_1->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE | FL_ALIGN_TOP); // Текст зверху зліва

    value_box_2 = new Fl_Box(margin + box_w + gap, margin, box_w, box_h, "NO DATA 2");
    value_box_2->box(FL_DOWN_BOX);
    value_box_2->color(FL_WHITE);
    value_box_2->labelsize(12);
    value_box_2->labelfont(FL_BOLD);
    value_box_2->align(FL_ALIGN_LEFT | FL_ALIGN_INSIDE | FL_ALIGN_TOP);


    copy_button = new Fl_Button(_width / 2 - 75, _height - 40, 150, 30, "COPY ALL");
    copy_button->callback(copy_callback, this);

    window->end();
    window->show();

    Fl::add_timeout(0.1, update_callback, this);

    while (is_running && window->shown())
    {
        Fl::wait();
    }
}

inline void DebugWindow::update_callback(void* data)
{
    DebugWindow* instance = static_cast<DebugWindow*>(data);

    if (instance->is_running)
    {
        instance->redraw_widget();
        Fl::repeat_timeout(0.1, update_callback, data);
    }
}

inline void DebugWindow::redraw_widget()
{
    std::string val1, val2;

    {
        std::lock_guard<std::mutex> lock(value_mutex);
        val1 = current_value_1;
        val2 = current_value_2;
    }

    value_box_1->copy_label(val1.c_str());
    value_box_2->copy_label(val2.c_str());

    Fl::flush();
}

inline void DebugWindow::copy_callback(Fl_Widget* w, void* data)
{
    DebugWindow* instance = static_cast<DebugWindow*>(data);

    std::string text_1 = instance->value_box_1->label() ? instance->value_box_1->label() : "";
    std::string text_2 = instance->value_box_2->label() ? instance->value_box_2->label() : "";

    // Формуємо текст для буфера: ліва колонка, розділювач, права колонка
    std::string combined_text = "=== LEFT COLUMN ===\n" + text_1 + "\n\n=== RIGHT COLUMN ===\n" + text_2;

    if (!combined_text.empty())
    {
        // Просте екранування для bash
        std::string safe_text;
        for (char c : combined_text) {
            if (c == '\'') safe_text += "'\\''";
            else safe_text += c;
        }

        std::string command = "echo '" + safe_text + "' | xclip -selection clipboard";
        system(command.c_str());
    }
}

#endif // DEBUGWINDOW_H
