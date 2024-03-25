# Xây dựng hệ thống nhận dạng món ăn đặc sản Việt Nam

Bài toán object detection là một trong những bài toán của lĩnh vực thị giác máy tính và trí tuệ nhân tạo. Nhiệm vụ chính của object detection là phát hiện và xác định vị trí của các đối tượng trong ảnh hoặc video.

Cụ thể, trong bài toán này, một hệ thống phải nhận diện và vẽ ra các khung (bounding boxes) xung quanh các đối tượng trong hình ảnh, đồng thời phân loại chúng thành các lớp đã được định nghĩa trước.

Project này sẽ xây dựng một mô hình máy học có khả năng nhận dạng được các thành phần nguyên liệu xuất hiện trong hình ảnh của món ăn. Từ danh sách các nguyên liệu được nhận dạng có thể đưa ra dự đoán món ăn trong ảnh là món gì.

**Link dataset:** https://mega.nz/folder/Ne81mCqR#2fcJjE-sN-zVud0ssOAAdA

## YOLO:
YOLO, viết tắt của "You Only Look Once", là một trong những mô hình quan trọng và phổ biến trong lĩnh vực object detection. YOLO tiêu biểu cho sự tiến bộ của deep learning trong việc giải quyết bài toán object detection một cách hiệu quả và nhanh chóng.

Một trong những ưu điểm lớn của YOLO so với các phương pháp truyền thống là tốc độ xử lý nhanh, vì nó có thể dự đoán tất cả các bounding boxes trong một lần chạy. Điều này làm cho YOLO rất phù hợp cho các ứng dụng thời gian thực.

## Các bước thực hiện dự án:
1. Chuẩn bị dataset để huấn luyện mô hình YOLO. Ảnh của các món ăn được download từ Google Image và ảnh chụp thực tế. Dữ liệu được gán nhãn bằng LabelImg.

[Hướng dẫn download và install LabelImg](https://thigiacmaytinh.com/su-dung-tool-labelimg-de-danh-nhan-vat-the-trong-hinh/)

2. Chia dữ liệu ra làm 3 phần: **train, valid, test.**
3. Huấn luyện mô hình YOLO. Phiên bản được sử dụng là Yolov8.
```
yolo task=detect mode=train model=yolov8x.pt data=/content/drive/MyDrive/Computer_Vision/NLN/demo/dataset_food/cfg.yaml epochs=28
```
- **task:** đối số chỉ định nhiệm vụ mà mô hình sẽ thực hiện, trong trường hợp này là phát hiện vật thể.
- **mode:** đối số chỉ định chế độ hoạt động của mô hình, ở đây là chế độ huấn luyện.
- **model:**  đối số chỉ định mô hình cụ thể mà mô hình YOLO sử dụng. Trong trường hợp này, đó là mô hình có tên "yolov8x.pt".
- **data:** đối số  chỉ định đường dẫn tới dữ liệu đào tạo hoặc cấu hình cần thiết cho mô hình. Trong trường hợp này, đường dẫn này dẫn tới một tệp cấu hình YAML.
- **epochs:** đối số chỉ định số lượng epochs (vòng lặp qua toàn bộ dữ liệu đào tạo) mà mô hình sẽ được huấn luyện.
4. Kiểm tra độ chính xác của mô hình bằng cách dự đoán phần tử mới.
5. Một món ăn sẽ được chia gồm hai thành phần: **Nguyên liệu chính** và **Nguyên liệu phụ**. Danh sách các nguyên liệu chính và phụ sẽ được dùng xem như **Bộ luật** để dự đoán món ăn. Mô hình Yolo sẽ phát hiện đồng thời dự đoán nhãn cho các đối tượng nguyên liệu trong ảnh. Danh sách các nhãn này sẽ được so sánh với **Bộ luật** để đưa ra dự đoán tên của món ăn.
Ảnh bộ luật:
![example](./example_images/excel.JPG)
6. Triển khai mô hình thành web service. Xây dựng ứng dụng web với Backend là **Flask** và Frontend là **Vuejs, thư viện UI Vuetify.**

## Cách dự đoán món ăn
Đo khoảng cách giữa tập thành phần nguyên liệu được dự đoán với tập thành phần nguyên liệu chính + phụ của các món ăn khác.

Ví dụ: Yolo phát hiện ra được tập thành phần nguyên liệu gồm **detect = {"bún", "thịt bò"}**

![example](./example_images/excel.JPG)
Xét hàng đầu tiên (Bún cá) trong bộ luật: các nguyên liệu chính gồm "bún", "cá"

phần tử "bún" của detect **thuộc** bộ luật của bún cá => distance = 0

phần tử "cá" của detect **không thuộc** bộ luật của bún cá => distance = 0 + 1 = 1

Xét hàng thứ 2 (Hủ tiếu Nam Vang) trong bộ luật: các nguyên liệu chính gồm "hủ tiếu", "tôm", "trứng", "thịt băm"; các nguyên liệu phụ gồm "mực", "thịt heo"

phần tử "bún" của detect **không thuộc** bộ luật của hủ tiếu Nam Vang => distance = 1

phần tử "cá" của detect **không thuộc** bộ luật của hủ tiếu Nam Vang => distance = 1 + 1 = 2

Các phần tử của detect cũng **không thuộc** thành phần nguyên liệu phụ của Hủ tiếu Nam Vang => distance không thay đổi

Xét hàng thứ 3 (Hủ tiếu Mỹ Tho) trong bộ luật: các nguyên liệu chính gồm "hủ tiếu", "tôm", "thịt heo", "gan"; các nguyên liệu phụ gồm "trứng", "thịt băm", "mực"

phần tử "bún" của detect **không thuộc** bộ luật của hủ tiếu Mỹ Tho => distance = 1

phần tử "cá" của detect **không thuộc** bộ luật của hủ tiếu Mỹ Tho => distance = 1 + 1 = 2

Các phần tử của detect cũng **không thuộc** thành phần nguyên liệu phụ của Hủ tiếu Mỹ Tho => distance không thay đổi

...

Xét hàng cuối cùng (Bún đậu mắm tôm) trong bộ luật: các nguyên liệu chính gồm "bún", "chả cốm", "dồi sụn", "đậu hũ", "thịt heo", "chả giò"

phần tử "bún" của detect **không thuộc** bộ luật của bún đậu mắm tôm => distance = 1

phần tử "cá" của detect **không thuộc** bộ luật của bún đậu mắm tôm => distance = 1 + 1 = 2

### Khoảng cách giữa detect và món ăn nào có giá trị ngắn nhất (nhỏ nhất) thì đó là món ăn được dự đoán.

## Kết quả Demo:
![example](./example_images/test1.JPG)
![example](./example_images/test2.JPG)
![example](./example_images/test3.JPG)

## Hướng phát triển của dự án:
1. Huấn luyện thêm mô hình CNN để phân lớp lại (xác thực) nhãn mà Yolo đã detect dược.
2. **Belief merge**, hay **hợp nhất niềm tin**, là một kỹ thuật trong trí tuệ nhân tạo được sử dụng để kết hợp thông tin từ nhiều nguồn khác nhau. Bài toán của chúng ta sẽ huấn luyện thêm các mô hình object detection khác (ngoài Yolo). Các mô hình này cũng sẽ đưa ra dự đoán về nguyên liệu trong ảnh món ăn. Kết hợp các thông tin từ **các mô hình object detection** này giúp đưa ra dự đoán về món ăn chính xác hơn.