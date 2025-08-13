def get_scale(img, page_rect):
    img_w, img_h = img.size
    scale_x = page_rect.width / img_w
    scale_y = page_rect.height / img_h
    return scale_x, scale_y
