# 프롬프트 데이터 일람
챗봇의 chat completion에 활용하기 위한 프롬프트 데이터입니다.

## 경로별 설명
- `original_data/`: 과제를 위해 전달 받은 raw data를 담고 있습니다. 각 문서는 정제되지 않은 Markdown 문서의 형식을 가지고 있습니다.
- `refined_data/`: `original_data/` 아래에 있는 문서들을 JSON 문서로 바꿔 작성한 파일들을 담고 있습니다.
- `refined_data_for_embedding/`: `refined_data/` 아래에 있는 문서들을 임베딩화하기 좋은 단위로 나눈 파일들을 담고 있습니다.

## refined\_data\_for\_embedding 폴더의 구성
`index.json` 파일 안에, 각 문서별로 구획이 어떻게 나눠져 있는지 나타내는 데이터가 있습니다.

```json
{
    "project_data_카카오톡채널.json": [
        "project_data_카카오톡채널_introduction.json",
        "project_data_카카오톡채널_functionalities.json"
    ],
    "project_data_카카오싱크.json": [
        "..."
    ]
}
```

예를 들어, `refined_data/project_data_카카오톡채널.json`의 임베딩을 위한 구획을 가져오고 싶다면,
`redfined_data_for_embedding/index.json`에서 `project_data_카카오톡채널.json` 키 값으로 리스트를 가져온 후,
`refined_data_for_embedding/` 아래에서 리스트 안에 있는 모든 파일을 가져와 임베딩으로 변환하면 됩니다.

임베딩화한 데이터는 벡터 DB에 넣어서 가져오는 방식으로 사용할 수 있습니다.
