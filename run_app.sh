# 完整序列
python app.py \
    --attention-filename complete_attention_matrix \
    --time-series-filename complete_time_series \
    --separate-time-series-legend \
    --separate-attention-colorbar \
    --attention-matrix-name ATTENTION_MATRIX_COMPLETE \
    --mask-name MASK_COMPLETE

# 缺失序列
python app.py \
    --attention-filename missing_attention_matrix \
    --time-series-filename missing_time_series \
    --separate-time-series-legend \
    --separate-attention-colorbar \
    --attention-matrix-name ATTENTION_MATRIX_MISSING \
    --mask-name MASK_MISSING